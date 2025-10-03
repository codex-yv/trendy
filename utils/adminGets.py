from configs.trendyDB import client

async def get_users():
    db = client["Clients"]
    colls = await db.list_collection_names()  # FIXED

    users_dict = {}

    for coll in colls:
        collection = db[coll]

        user_data = await collection.find({}, {"_id": 0}).to_list(None)

        if user_data:
            user_desc = user_data[0]['fullname'] + " - " + user_data[0]['team']
            users_dict[coll] = user_desc

    return users_dict

async def get_projects():
    db = client["Activity"]
    collection = db["Projects"]

    docs = await collection.find().to_list(None)

    project_list = []

    for doc in docs:
        project = {"project_name":doc['project_name'], "initiated_date":doc['initiated_date'], "due_date":doc['due_date'], 
                "team":doc['team'], "Status":doc['status'], "assigned_member": doc['assigned_members'], "project_manager":doc['project_manager'], "components":doc['components']}

        project_list.append(project)
    
    return project_list