import os, boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from botocore.config import Config
import json
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "ap-southeast-2")
SERVICE = "aoss"  # Serverless
OS_ENDPOINT = os.environ["OS_ENDPOINT"]  # e.g., https://abc123.ap-southeast-2.aoss.amazonaws.com
HOST = OS_ENDPOINT.replace("https://", "")

auth = AWSV4SignerAuth(boto3.Session().get_credentials(), REGION, SERVICE)

os_client = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=auth,
    use_ssl=True, verify_certs=True,
    connection_class=RequestsHttpConnection,
)

INDEX = "courses-v1"
DIM = 1024  # Titan v2 output dimension

mapping = {
    "settings": {"index": {"knn": True}},
    "mappings": {
        "properties": {
            "uuid": {"type": "keyword"},
            "vector": {
                "type": "knn_vector",
                "dimension": DIM,
                "method": {"name": "hnsw", "space_type": "cosinesimil"}
            },
            "title": {"type": "text"},
            "subject_primary": {"type": "text"},
            "partner_primary": {"type": "text"},
            "level": {"type": "keyword"},
            "skills": {"type": "text"},
            "plaform": {"type": "keyword"},
            "last_updated": {"type": "date"}  # Add for sync tracking
        }
    }
}

# Delete existing index if it exists to clear any conflicting mappings
if os_client.indices.exists(index=INDEX):
    print(f"Deleting existing index: {INDEX}")
    os_client.indices.delete(index=INDEX)
    
# Create fresh index with clean mapping
print(f"Creating fresh index: {INDEX}")
os_client.indices.create(index=INDEX, body=mapping)

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
MODEL_ID = "amazon.titan-embed-text-v2:0"

def embed_text(text: str) -> list[float]:
    payload = {"inputText": text}
    resp = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )
    body = json.loads(resp["body"].read())
    return body["embedding"]

ddb = boto3.resource("dynamodb", region_name=REGION).Table(os.getenv("DDB_TABLE", "Courses"))

def build_text(it: dict) -> str:
    # Fixed: Handle null skills properly and array level
    level_str = ""
    level_value = it.get('level')
    if isinstance(level_value, list) and level_value:
        level_str = f"Level: {level_value[0]}"
    elif level_value:
        level_str = f"Level: {level_value}"
    
    parts = [
        it.get("title") or "",
        it.get("primary_description") or "",
        it.get("secondary_description") or "",
        "Partners: " + ", ".join(it.get("partners", [])) if it.get("partners") else "",
        "Subjects: " + ", ".join(it.get("subjects", [])) if it.get("subjects") else "",
        level_str,
        f"Language: {it.get('lang') or it.get('language') or ''}",
        f"Platform: {it.get('platform') or ''}"
    ]
    # Only add skills if it exists and is not a null representation
    skills = it.get('skills')
    if skills:
        if isinstance(skills, list):
            # Filter out null values from list
            valid_skills = [str(s) for s in skills if s not in ["null", None, ""]]
            if valid_skills:
                parts.append(f"Skills: {', '.join(valid_skills)}")
        elif isinstance(skills, str) and skills not in ["['null']", "null", "None", ""]:
            parts.append(f"Skills: {skills}")
        elif isinstance(skills, dict):
            # Convert dict to readable string
            parts.append(f"Skills: {json.dumps(skills)}")
    
    return "\n".join([p for p in parts if p]).strip()

def upsert_course(course_item):
    """Upsert a single course to the vector index"""
    try:
        vec = embed_text(build_text(course_item))
        
        # Clean and validate all fields before indexing
        doc = {
            "uuid": course_item["uuid"],
            "vector": vec,
            "title": course_item.get("title") or "",
            "subject_primary": course_item.get("subject_primary") or "",
            "partner_primary": course_item.get("partner_primary") or "",
            "platform": course_item.get("platform") or "",
            "last_updated": course_item.get("last_updated", course_item.get("updated_at"))
        }
        
        # Handle level field - convert array to string if needed
        level_value = course_item.get("level")
        if isinstance(level_value, list) and level_value:
            doc["level"] = level_value[0]  # Take first element
        elif level_value:
            doc["level"] = str(level_value)
        else:
            doc["level"] = ""
        
        # Handle skills field - add back with proper handling
        try:
            skills_value = course_item.get("skills")
            if skills_value:
                if isinstance(skills_value, list):
                    # Join list elements, filter out nulls
                    valid_skills = [str(s) for s in skills_value if str(s) not in ["null", "None", ""]]
                    doc["skills"] = ", ".join(valid_skills) if valid_skills else ""
                else:
                    # Convert to string, handle null representations
                    skills_str = str(skills_value)
                    doc["skills"] = skills_str if skills_str not in ["null", "None", "['null']"] else ""
            else:
                doc["skills"] = ""
        except Exception:
            # If anything goes wrong with skills, just set it to empty
            doc["skills"] = ""
        
        # For Serverless, just index the document
        os_client.index(index=INDEX, body=doc)
        print(f"Indexed course: {course_item['uuid']}")
            
    except Exception as e:
        print(f"Error processing course {course_item.get('uuid')}: {e}")

def backfill(limit_per_page=500):
    """Initial backfill of all courses"""
    scan_kwargs = {"Limit": limit_per_page}
    processed = 0
    
    while True:
        resp = ddb.scan(**scan_kwargs)
        for it in resp["Items"]:
            upsert_course(it)
            processed += 1
            
        print(f"Processed {processed} courses...")
        
        if "LastEvaluatedKey" not in resp:
            break
        scan_kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    
    print(f"Backfill complete: {processed} courses indexed")
    # Note: OpenSearch Serverless doesn't support explicit refresh

def sync_updates(since_timestamp=None):
    """Sync only updated courses since timestamp"""
    if since_timestamp:
        # Query DDB for courses updated since timestamp
        # You'll need to implement this based on your DDB schema
        pass
    else:
        # Full backfill
        backfill()

def search_courses(query_text: str, k: int = 5) -> list:
    """Search for similar courses"""
    query_vector = embed_text(query_text)
    
    search_body = {
        "query": {
            "knn": {
                "vector": {
                    "vector": query_vector,
                    "k": k
                }
            }
        },
        "_source": ["uuid", "title", "subject_primary", "partner_primary", "level", "platform", "skills"],
        "size": k
    }
    
    response = os_client.search(index=INDEX, body=search_body)
    return [
        {
            "uuid": hit["_source"]["uuid"],
            "score": hit["_score"],
            "title": hit["_source"]["title"],
            "subject_primary": hit["_source"]["subject_primary"],
            "partner_primary": hit["_source"]["partner_primary"],
            "level": hit["_source"]["level"],
            "platform": hit["_source"]["platform"],
            "skills": hit["_source"]["skills"]
        }
        for hit in response["hits"]["hits"]
    ]

def get_index_count():
    """Get the total number of documents in the index"""
    try:
        response = os_client.count(index=INDEX)
        count = response["count"]
        print(f"Total documents in index '{INDEX}': {count}")
        return count
    except Exception as e:
        print(f"Error getting count: {e}")
        return 0

def check_for_duplicates():
    """Check for duplicate UUIDs in the index"""
    try:
        # Aggregation to count documents per UUID
        agg_body = {
            "size": 0,
            "aggs": {
                "uuid_counts": {
                    "terms": {
                        "field": "uuid",
                        "size": 10000  # Adjust based on your data size
                    }
                }
            }
        }
        
        response = os_client.search(index=INDEX, body=agg_body)
        uuid_counts = response["aggregations"]["uuid_counts"]["buckets"]
        
        duplicates = [bucket for bucket in uuid_counts if bucket["doc_count"] > 1]
        
        if duplicates:
            print(f"Found {len(duplicates)} UUIDs with duplicates:")
            for dup in duplicates[:10]:  # Show first 10
                print(f"  UUID {dup['key']}: {dup['doc_count']} documents")
        else:
            print("No duplicates found")
            
        return duplicates
        
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return []

def clean_duplicates():
    """Remove duplicate documents, keeping only one per UUID"""
    try:
        duplicates = check_for_duplicates()
        if not duplicates:
            print("No duplicates to clean")
            return
            
        for dup in duplicates:
            uuid = dup["key"]
            print(f"Cleaning duplicates for UUID: {uuid}")
            
            # Find all documents with this UUID
            query = {
                "query": {"term": {"uuid": uuid}},
                "size": 100,
                "sort": [{"_id": "asc"}]  # Sort to keep consistent document
            }
            
            response = os_client.search(index=INDEX, body=query)
            docs = response["hits"]["hits"]
            
            # Keep the first document, delete the rest
            for doc in docs[1:]:  # Skip first, delete others
                os_client.delete(index=INDEX, id=doc["_id"])
                
            print(f"  Kept 1, deleted {len(docs)-1} duplicates for {uuid}")
            
    except Exception as e:
        print(f"Error cleaning duplicates: {e}")

def delete_course_by_uuid(uuid: str):
    """Delete course documents by UUID"""
    query = {
        "query": {"term": {"uuid": uuid}},
        "size": 100  # In case there are duplicates
    }
    
    # Find all documents with this UUID
    response = os_client.search(index=INDEX, body=query)
    
    # Delete each document
    for hit in response["hits"]["hits"]:
        os_client.delete(index=INDEX, id=hit["_id"])
    
    print(f"Deleted documents for course: {uuid}")
    
    # Delete each document
    for hit in response["hits"]["hits"]:
        os_client.delete(index=INDEX, id=hit["_id"])
    
    print(f"Deleted documents for course: {uuid}")

def sync_course(course_item):
    """Sync a single course (delete old, add new)"""
    # Delete existing versions
    delete_course_by_uuid(course_item["uuid"])
    
    # Add updated version
    upsert_course(course_item)

def rag_search(query: str, k: int = 5):
    """RAG workflow: Vector search + DynamoDB lookup"""
    # 1. Vector search for relevant courses
    similar_courses = search_courses(query, k)
    
    # 2. Fetch full details from DynamoDB
    course_details = []
    for course in similar_courses:
        try:
            full_course = ddb.get_item(Key={"uuid": course["uuid"]})["Item"]
            full_course["similarity_score"] = course["score"]
            course_details.append(full_course)
        except Exception as e:
            print(f"Could not fetch course {course['uuid']}: {e}")
    
    return course_details

if __name__ == "__main__":
    backfill()
    # First, check current state
    print("=== DIAGNOSTIC INFO ===")
    get_index_count()
    
    # Check for duplicates
    print("\n=== CHECKING FOR DUPLICATES ===")
    duplicates = check_for_duplicates()
    
    if duplicates:
        print("\n=== CLEANING DUPLICATES ===")
        clean_duplicates()
        print("\n=== FINAL COUNT AFTER CLEANUP ===")
        get_index_count()
    else:
        print("\nNo duplicates found - counts should match DynamoDB")
    
    # Uncomment below to run backfill
    