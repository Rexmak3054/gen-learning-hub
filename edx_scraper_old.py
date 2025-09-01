import os
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from playwright.sync_api import sync_playwright, Playwright

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
DDB_TABLE  = os.getenv("DDB_TABLE", "Courses")

course_info: List[Dict[str, Any]] = []

def _to_number(n) -> Decimal:
    try:
        return Decimal(str(int(n)))
    except Exception:
        return Decimal("0")

def _as_list(v: Any) -> List[str]:
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

def _primary_or_none(values: List[str]) -> Optional[str]:
    return values[0] if values else None

def _map_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    uuid = str(item.get("uuid", "")).strip()
    if not uuid:
        return None

    partners = _as_list(item.get("partner"))
    subjects = _as_list(item.get("subject"))

    mapped: Dict[str, Any] = {
        "uuid": uuid,  # PK
        "title": item.get("title"),
        "img_url": item.get("card_image_url"),
        "lang": item.get("language"),
        "learning_type": item.get("learning_type"),
        "level": item.get("level"),
        "primary_description": item.get("primary_description"),
        "secondary_description": item.get("secondary_description"),
        "url": item.get("marketing_url"),
        "enrol_cnt": _to_number(item.get("recent_enrollment_count")),
        "weeks_to_complete": _to_number(item.get("weeks_to_complete")),
        "plaform": 'edx',
        # Store full lists
        "partners": partners,          # List[str]
        "subjects": subjects,          # List[str]
    }

    # Scalar keys for GSIs (String)
    partner_primary = _primary_or_none(partners)
    subject_primary = _primary_or_none(subjects)

    if partner_primary:
        mapped["partner_primary"] = partner_primary  # <- use this for PartnerIndex
        # If your GSI is currently on 'partner', also mirror it:
        # mapped["partner"] = partner_primary

    if subject_primary:
        mapped["subject_primary"] = subject_primary  # <- use this for SubjectIndex
        # If your GSI is currently on 'subject', also mirror it:
        # mapped["subject"] = subject_primary

    return mapped

def handle_response(response):
    if "queries" in response.url and response.status == 200:
        try:
            json_data = response.json()
            hits = (json_data.get("results", []) or [{}])[0].get("hits", [])
            added = 0
            for raw in hits:
                mapped = _map_item(raw)
                if mapped:
                    course_info.append(mapped)
                    added += 1
            print(f"✅ Captured {len(hits)} hits; mapped {added} (running total: {len(course_info)})")
        except Exception as e:
            print(f"⚠️  Non-JSON response or parse error: {e}")

def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.on("response", handle_response)
    page.goto("https://www.edx.org/search?q=ai&tab=course&page=1")
    page.wait_for_timeout(5000)
    browser.close()

def save_to_dynamodb(items: List[Dict[str, Any]]):
    if not items:
        print("No items to write.")
        return
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = ddb.Table(DDB_TABLE)

    with table.batch_writer(overwrite_by_pkeys=["uuid"]) as batch:
        for it in items:
            batch.put_item(Item=it)

    print(f"🗄️  Wrote {len(items)} items to DynamoDB table '{DDB_TABLE}' in {AWS_REGION}.")

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw)
    print(f"Total scraped items (post-map): {len(course_info)}")
    save_to_dynamodb(course_info)