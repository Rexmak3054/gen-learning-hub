import requests
import json
from typing import Any, Dict, List, Optional
from decimal import Decimal
from course_info_handler import CourseStore

class CourseraScraper:
    def __init__(self):
        pass
    def query(self, keywords):

        url = "https://www.coursera.org/graphql-gateway?opname=Search"

        payload = json.dumps([
        {
            "operationName": "Search",
            "variables": {
            "requests": [
                {
                "entityType": "PRODUCTS",
                "limit": 20,
                "disableRecommender": True,
                "maxValuesPerFacet": 1000,
                "facetFilters": [],
                "cursor": "0",
                "query": keywords
                },
            
            ]
            },
            "query": "query Search($requests: [Search_Request!]!) {\n  SearchResult {\n    search(requests: $requests) {\n      ...SearchResult\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SearchResult on Search_Result {\n  elements {\n    ...SearchHit\n    __typename\n  }\n  facets {\n    ...SearchFacets\n    __typename\n  }\n  pagination {\n    cursor\n    totalElements\n    __typename\n  }\n  totalPages\n  source {\n    indexName\n    recommender {\n      context\n      hash\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SearchHit on Search_Hit {\n  ...SearchArticleHit\n  ...SearchProductHit\n  ...SearchSuggestionHit\n  __typename\n}\n\nfragment SearchArticleHit on Search_ArticleHit {\n  aeName\n  careerField\n  category\n  createdByName\n  firstPublishedAt\n  id\n  internalContentEpic\n  internalProductLine\n  internalTargetKw\n  introduction\n  islocalized\n  lastPublishedAt\n  localizedCountryCd\n  localizedLanguageCd\n  name\n  subcategory\n  topics\n  url\n  skill: skills\n  __typename\n}\n\nfragment SearchProductHit on Search_ProductHit {\n  avgProductRating\n  cobrandingEnabled\n  completions\n  duration\n  id\n  imageUrl\n  isCourseFree\n  isCreditEligible\n  isNewContent\n  isPartOfCourseraPlus\n  name\n  numProductRatings\n  parentCourseName\n  parentLessonName\n  partnerLogos\n  partners\n  productCard {\n    ...SearchProductCard\n    __typename\n  }\n  productDifficultyLevel\n  productDuration\n  productType\n  skills\n  url\n  videosInLesson\n  translatedName\n  translatedSkills\n  translatedParentCourseName\n  translatedParentLessonName\n  tagline\n  fullyTranslatedLanguages\n  subtitlesOnlyLanguages\n  __typename\n}\n\nfragment SearchSuggestionHit on Search_SuggestionHit {\n  id\n  name\n  score\n  __typename\n}\n\nfragment SearchProductCard on ProductCard_ProductCard {\n  id\n  canonicalType\n  marketingProductType\n  badges\n  productTypeAttributes {\n    ... on ProductCard_Specialization {\n      ...SearchProductCardSpecialization\n      __typename\n    }\n    ... on ProductCard_Course {\n      ...SearchProductCardCourse\n      __typename\n    }\n    ... on ProductCard_Clip {\n      ...SearchProductCardClip\n      __typename\n    }\n    ... on ProductCard_Degree {\n      ...SearchProductCardDegree\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SearchProductCardSpecialization on ProductCard_Specialization {\n  isPathwayContent\n  __typename\n}\n\nfragment SearchProductCardCourse on ProductCard_Course {\n  isPathwayContent\n  rating\n  reviewCount\n  __typename\n}\n\nfragment SearchProductCardClip on ProductCard_Clip {\n  canonical {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment SearchProductCardDegree on ProductCard_Degree {\n  canonical {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment SearchFacets on Search_Facet {\n  name\n  nameDisplay\n  valuesAndCounts {\n    ...ValuesAndCounts\n    __typename\n  }\n  __typename\n}\n\nfragment ValuesAndCounts on Search_FacetValueAndCount {\n  count\n  value\n  valueDisplay\n  __typename\n}\n"
        }
        ])
        headers = {
        'content-type': 'application/json',
        'Cookie': 'CSRF3-Token=1757302417.ghSMbGuOlpb5QpbD; __204u=9042918874-1756438417216'
        }

        response = requests.request("POST", url, headers=headers, data=payload)



        # response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response = json.loads(response.text)
        return response[0]['data']['SearchResult']['search'][0]['elements']

    def _to_number(self, n) -> Decimal:
        try:
            return Decimal(str(int(n)))
        except Exception:
            return Decimal("0")

    def _as_list(self,v: Any) -> List[str]:
        """Coerce value into a clean list[str]."""
        if v is None:
            return []
        if isinstance(v, list):
            out = []
            for el in v:
                if isinstance(el, str):
                    s = el.strip()
                    if s:
                        out.append(s)
                elif isinstance(el, dict):
                    # try common name keys
                    for k in ("name", "title", "partner", "provider", "display_name"):
                        val = el.get(k)
                        if isinstance(val, str) and val.strip():
                            out.append(val.strip())
                            break
            # de-dup, preserve order
            seen = set()
            deduped = []
            for s in out:
                if s not in seen:
                    seen.add(s)
                    deduped.append(s)
            return deduped
        if isinstance(v, str):
            s = v.strip()
            return [s] if s else []
        # numbers to string (rare)
        if isinstance(v, (int, float, Decimal)):
            return [str(v)]
        return []

    def _primary_or_none(self,values: List[str]) -> Optional[str]:
        return values[0] if values else None

    def _map_item(self,item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        uuid = str(item.get("id", "")).strip()
        if not uuid:
            return None

        partners = self._as_list(item.get("partners"))
        
        subjects = item.get("skills", ['NA'])
        mapped: Dict[str, Any] = {
            "uuid": uuid,  # PK
            "title": item.get("name"),
            "img_url": item.get("imageUrl"),
            "partnerLogos": item.get("partnerLogos"), 
            "lang": item.get("fullyTranslatedLanguages"),
            "learning_type": item.get("productCard").get('marketingProductType'),
            "level": item.get("productDifficultyLevel"),
            "primary_description": item.get("tagline"),
            "url": 'https://www.coursera.org'+item.get("url"),
            "duration": item.get("productDuration"),
            "platform": 'coursera',
            "product": item.get("productCard").get('marketingProductType'),
            "skills": item.get("skills"),
            # Store full lists
            "partners": partners,          # List[str]
            # "subjects": subjects,          # List[str]
        }

        # Scalar keys for GSIs (String)
        partner_primary = self._primary_or_none(partners)
        subject_primary = self._primary_or_none(subjects)

        if partner_primary:
            mapped["partner_primary"] = partner_primary  # <- use this for PartnerIndex

        if subject_primary:
            mapped["subject_primary"] = subject_primary  # <- use this for SubjectIndex
    
        return mapped

    def handle_response(self,resp):
        course_info: List[Dict[str, Any]] = []
        
        added = 0
        
        for raw in resp:
            # try:
            mapped = self._map_item(raw)
            if mapped:
                course_info.append(mapped)
                added += 1
            # except Exception as e:
            #     print(f"⚠️  Non-JSON response or parse error: {e}")
        print(f"✅ Captured {len(resp)} hits; mapped {added} (running total: {len(course_info)})")

        return course_info



if __name__ == "__main__":
    scraper = CourseraScraper()
    resp = scraper.query('machine learning')
    course_info = scraper.handle_response(resp)
    print(course_info[0])
    store = CourseStore()
    store.put_many(course_info)