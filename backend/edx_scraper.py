import requests
import json
from typing import Any, Dict, List, Optional
from decimal import Decimal
from course_info_handler import CourseStore

class EdxScraper:
    def __init__(self):
        pass
    def query(self, keywords):

        url = "https://igsyv1z1xi-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(5.0.0)%3B%20Search%20(5.0.0)%3B%20Browser%3B%20instantsearch.js%20(4.78.1)%3B%20react%20(19.1.0-canary-029e8bd6-20250306)%3B%20react-instantsearch%20(7.15.5)%3B%20react-instantsearch-core%20(7.15.5)%3B%20next.js%20(15.2.3)%3B%20JS%20Helper%20(3.24.3)&x-algolia-api-key=6658746ce52e30dacfdd8ba5f8e8cf18&x-algolia-application-id=IGSYV1Z1XI"

        payload = {
        "requests": [
            {
            "indexName": "product",
            "clickAnalytics": True,
            "facets": [
                "ai_languages.transcription_languages",
                "ai_languages.translation_languages",
                "availability",
                "language",
                "learning_type",
                "level",
                "partner",
                "product",
                "program_type",
                "skills.skill",
                "subject",
                "fees"
            ],
            "filters": "(product:\"Course\" OR product:\"Program\" OR product:\"Executive Education\" OR product:\"2U Degree\") AND (blocked_in:null OR NOT blocked_in:\"AU\") AND (allowed_in:null OR allowed_in:\"AU\")",
            "hitsPerPage": 24,
            "maxValuesPerFacet": 100,
            "query": keywords
            },
            {
            "indexName": "product",
            "clickAnalytics": True,
            "facetFilters": [
                "product:Program"
            ],
            "facets": [
                "ai_languages.transcription_languages",
                "ai_languages.translation_languages",
                "availability",
                "language",
                "learning_type",
                "level",
                "partner",
                "product",
                "program_type",
                "skills.skill",
                "subject"
            ],
            "filters": "(product:\"Course\" OR product:\"Program\" OR product:\"Executive Education\" OR product:\"2U Degree\") AND (blocked_in:null OR NOT blocked_in:\"AU\") AND (allowed_in:null OR allowed_in:\"AU\")",
            "highlightPostTag": "__/ais-highlight__",
            "highlightPreTag": "__ais-highlight__",
            "hitsPerPage": 3,
            "maxValuesPerFacet": 100,
            "query": keywords
            },
            {
            "indexName": "product",
            "clickAnalytics": True,
            "facetFilters": [
                "product:Course"
            ],
            "facets": [
                "ai_languages.transcription_languages",
                "ai_languages.translation_languages",
                "availability",
                "language",
                "learning_type",
                "level",
                "partner",
                "product",
                "program_type",
                "skills.skill",
                "subject"
            ],
            "filters": "(product:\"Course\" OR product:\"Program\" OR product:\"Executive Education\" OR product:\"2U Degree\") AND (blocked_in:null OR NOT blocked_in:\"AU\") AND (allowed_in:null OR allowed_in:\"AU\")",
            "highlightPostTag": "__/ais-highlight__",
            "highlightPreTag": "__ais-highlight__",
            "hitsPerPage": 3,
            "maxValuesPerFacet": 100,
            "query": keywords
            },
            {
            "indexName": "product",
            "clickAnalytics": True,
            "facetFilters": [
                "product:Executive Education"
            ],
            "facets": [
                "ai_languages.transcription_languages",
                "ai_languages.translation_languages",
                "availability",
                "language",
                "learning_type",
                "level",
                "partner",
                "product",
                "program_type",
                "skills.skill",
                "subject"
            ],
            "filters": "(product:\"Course\" OR product:\"Program\" OR product:\"Executive Education\" OR product:\"2U Degree\") AND (blocked_in:null OR NOT blocked_in:\"AU\") AND (allowed_in:null OR allowed_in:\"AU\")",
            "highlightPostTag": "__/ais-highlight__",
            "highlightPreTag": "__ais-highlight__",
            "hitsPerPage": 3,
            "maxValuesPerFacet": 100,
            "query": keywords
            },
            {
            "indexName": "product",
            "clickAnalytics": True,
            "facetFilters": [
                "product:2U Degree"
            ],
            "facets": [
                "ai_languages.transcription_languages",
                "ai_languages.translation_languages",
                "availability",
                "language",
                "learning_type",
                "level",
                "partner",
                "product",
                "program_type",
                "skills.skill",
                "subject"
            ],
            "filters": "(product:\"Course\" OR product:\"Program\" OR product:\"Executive Education\" OR product:\"2U Degree\") AND (blocked_in:null OR NOT blocked_in:\"AU\") AND (allowed_in:null OR allowed_in:\"AU\")",
            "highlightPostTag": "__/ais-highlight__",
            "highlightPreTag": "__ais-highlight__",
            "hitsPerPage": 3,
            "maxValuesPerFacet": 100,
            "query": keywords
            }
        ]
        }
        headers = {
        'Content-Type': 'application/json; charset=UTF-8'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response = json.loads(response.text)
        return response['results']

    def _to_number(self,n) -> Decimal:
        try:
            return Decimal(str(int(n)))
        except Exception:
            return Decimal("0")

    def _as_list(self, v: Any) -> List[str]:
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

    def _primary_or_none(self, values: List[str]) -> Optional[str]:
        return values[0] if values else None

    def _map_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        uuid = str(item.get("uuid", "")).strip()
        if not uuid:
            return None

        partners = self._as_list(item.get("partner"))
        subjects = self._as_list(item.get("subject"))

        mapped: Dict[str, Any] = {
            "uuid": uuid,  # PK
            "title": item.get("title"),
            "img_url": item.get("card_image_url"),
            "partnerLogos": [o['logoImageUrl'] for o in item.get('owners')],
            "lang": item.get("language"),
            "learning_type": item.get("learning_type"),
            "level": item.get("level"),
            "primary_description": item.get("primary_description"),
            "secondary_description": item.get("secondary_description"),
            "url": item.get("marketing_url"),
            "enrol_cnt": self._to_number(item.get("recent_enrollment_count")),
            "weeks_to_complete": self._to_number(item.get("weeks_to_complete")),
            "platform": 'edx',
            "product": item.get("product"),
            "skills": item.get("skills"),
            # Store full lists
            "partners": partners,          # List[str]
            "subjects": subjects,          # List[str]
        }

        # Scalar keys for GSIs (String)
        partner_primary = self._primary_or_none(partners)
        subject_primary = self._primary_or_none(subjects)

        if partner_primary:
            mapped["partner_primary"] = partner_primary  # <- use this for PartnerIndex
            # If your GSI is currently on 'partner', also mirror it:
            # mapped["partner"] = partner_primary

        if subject_primary:
            mapped["subject_primary"] = subject_primary  # <- use this for SubjectIndex
            # If your GSI is currently on 'subject', also mirror it:
            # mapped["subject"] = subject_primary

        return mapped

    def handle_response(self,resp):
        course_info: List[Dict[str, Any]] = []
        try:
            for products in resp:
                added = 0
                hits = products.get("hits", [])
                for raw in hits:
                    mapped = self._map_item(raw)
                    if mapped:
                        course_info.append(mapped)
                        added += 1
                print(f"✅ Captured {len(hits)} hits; mapped {added} (running total: {len(course_info)})")
        except Exception as e:
            print(f"⚠️  Non-JSON response or parse error: {e}")
        return course_info



if __name__ == "__main__":
    scraper = EdxScraper()
    resp = scraper.query('AI')
    course_info = scraper.handle_response(resp)
    store = CourseStore()
    store.put_many(course_info)
