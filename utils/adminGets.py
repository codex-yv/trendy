from configs.trendyDB import client

async def get_users():
    db = client["Clients"]
    colls = await db.list_collection_names()  # FIXED

    users_dict = {}

    for coll in colls:
        collection = db[coll]

        user_data = await collection.find({}, {"_id": 0}).to_list(None)

        if user_data:
            if user_data[0]['action'] == 1: 
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
    
    return project_list[::-1]


async def get_tasks():
    db = client["Activity"]
    collection = db["Tasks"]

    docs = await collection.find().to_list(None)

    task_list = []

    for doc in docs:
        tasks = {"task_name":doc['task_name'], "initiated_date":doc['initiated_date'], "due_date":doc['due_date'], 
                "Status":doc['status'], "assigned_members": doc['assigned_members'], "desc":doc['desc']}

        task_list.append(tasks)
    
    return task_list[::-1]


async def get_projet_info():
    db = client["Activity"]
    collection = db["Projects"]

    docs = await collection.find().to_list(None)

    total_projects = len(docs)
    pd = 0 # projects done

    for doc in docs:
        if doc['status'] == 1:
            pd +=1

    return pd, total_projects

async def get_task_info():
    db = client["Activity"]
    collection = db["Tasks"]

    docs = await collection.find().to_list(None)

    total_tasks = len(docs)
    td = 0 # task done

    for doc in docs:
        if doc['status'] == 1:
            td +=1

    return td, total_tasks


async def get_users_for_approve():
    db = client["Clients"]
    collection_list = await db.list_collection_names()

    user_list = []

    for col in collection_list:
        collection = db[col]
        user_data = await collection.find({}, {"_id": 0}).to_list(None)

        if user_data:
            formatt = {"fullname":user_data[0]['fullname'], "email":user_data[0]['email'], "phone_number":user_data[0]['phone'], "role":user_data[0]['role'], "action":user_data[0]['action']}
            user_list.append(formatt)

    return user_list