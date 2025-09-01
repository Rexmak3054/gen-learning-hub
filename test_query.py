from course_info_handler import CourseStore

if __name__ == "__main__":
    store = CourseStore()
    
    resp = store.table.scan(
        FilterExpression="platform = :plt",
        ExpressionAttributeValues={":plt": "udemy"}
    )

    for it in resp["Items"]:
        print(it["uuid"], it["title"])