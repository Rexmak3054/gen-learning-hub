import requests
import json
from typing import Any, Dict, List, Optional
from decimal import Decimal
from course_info_handler import CourseStore

class UdemyScraper:
    def __init__(self):
        pass
    def query(self, keywords):

        url = "https://www.udemy.com/api/2024-01/graphql/"

        payload = json.dumps({
        "query": "\n    query SrpMxCourseSearch($query: String!, $page: NonNegativeInt!, $pageSize: MaxResultsPerPage!, $sortOrder: CourseSearchSortType, $filters: CourseSearchFilters, $context: CourseSearchContext) {\n  courseSearch(\n    query: $query\n    page: $page\n    pageSize: $pageSize\n    sortOrder: $sortOrder\n    filters: $filters\n    context: $context\n  ) {\n    count\n    results {\n      course {\n        badges {\n          __typename\n          name\n        }\n        curriculum {\n          contentCounts {\n            lecturesCount\n            practiceTestQuestionsCount\n          }\n        }\n        durationInSeconds\n        headline\n        id\n        images {\n          height125\n          px100x100\n          px240x135\n          px304x171\n          px480x270\n          px50x50\n        }\n        instructors {\n          id\n          name\n        }\n        isFree\n        isPracticeTestCourse\n        learningOutcomes\n        level\n        updatedOn\n        locale\n        rating {\n          average\n          count\n        }\n        title\n        urlAutoEnroll\n        urlCourseLanding\n        urlCourseTaking\n      }\n      trackingId\n      searchDebugFeatures\n      curriculumItemMatches {\n        __typename\n        ... on VideoLecture {\n          urlLanding\n        }\n        ... on PracticeAssignment {\n          urlLanding\n        }\n        ... on CodingExercise {\n          urlLanding\n        }\n        ... on PracticeTest {\n          urlLanding\n        }\n        ... on Quiz {\n          urlLanding\n        }\n        id\n        title\n      }\n    }\n    filterOptions {\n      label\n      key\n      buckets {\n        countWithFilterApplied\n        label\n        value\n        key\n        isSelected\n      }\n    }\n    page\n    pageCount\n    metadata {\n      querySuggestion {\n        query\n        type\n      }\n      hasOrgCourses\n      trackingId\n      originalQuery\n      experimentResults {\n        featureCode\n        experimentIds\n        configuration\n        isLocalDefault\n        isInExperiment\n      }\n      debug\n      associatedTopic {\n        id\n        url\n      }\n      certificationTopic {\n        url\n      }\n    }\n  }\n}\n    ",
        "variables": {
            "page": 0,
            "query": keywords,
            "sortOrder": "RELEVANCE",
            "pageSize": 20,
            "context": {
            "triggerType": "USER_QUERY"
            }
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'Cookie': '__cf_bm=ChrguKfkdb0o6vmeNXqWYogIVgb_FdB_XH_iIZslHoE-1756459934-1.0.1.1-f6ChnRo6Kv7_UXXt3aINEzNBSjAtFJ4ulIY8iTqiN7gsj_DB7AOKYCLWjw6MuGo6zSp9fULU0Zy.lWjNW_9w_gkQvHBqbqO6ffuPc8m8FEo; __cfruid=dac47636422f58f15c3de83716b89426c1ba6222-1756459934; __udmy_2_v57r=d8cf279035d74d168737e559f638b93e; ud_country_code=AU'
        }

        response = requests.request("POST", url, headers=headers, data=payload)



        # response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        response = json.loads(response.text)
        return response['data']['courseSearch']['results']

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
        uuid = str(item['course'].get("id", "")).strip()
        if not uuid:
            return None

        partners = [i['name'] for i in item['course'].get("instructors")]
        
        subjects = ['NA']
        mapped: Dict[str, Any] = {
            "uuid": uuid,  # PK
            "title": item['course'].get("title"),
            "img_url": item['course'].get("images")['px240x135'],
            "lang": item['course'].get("locale"),
            "learning_type": "Course",
            "level": item['course'].get("level"),
            "primary_description": item['course'].get("tagline"),
            "url": item['course'].get("urlCourseLanding"),
            "weeks_to_complete": self._to_number(item['course'].get("durationInSeconds")/60/2/5),
            "platform": 'udemy',
            "product": 'course',
            "skills": item['course'].get("learningOutcomes"),
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

    def handle_response(self, resp):
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
    scraper = UdemyScraper()
    resp = scraper.query('AI')
    course_info = scraper.handle_response(resp)
    print(course_info[0])
    store = CourseStore()
    store.put_many(course_info)