from configs.trendyDB import client
from security.decryptPass import decryptt
from bson import ObjectId

async def check_existing_user(collection_name):
    db = client["Clients"]
    collections = await db.list_collection_names()

    if collection_name in collections:
        return False
    else:
        return True


async def check_password(collection_name, password):
    db = client["Clients"]
    collection = db[collection_name]

    documents = await collection.find({}, {"_id": 0}).to_list(None)

    password_enc = documents[0]['password']
    key = documents[0]['key']

    password_dec = decryptt(token=password_enc, key = key)

    if password == password_dec:
        return True
    else:
        return False

async def get_username(collection_name):
    db = client["Clients"]
    collection = db[collection_name]
    documents = await collection.find({}, {"_id": 0}).to_list(None)
    fullname = documents[0]['fullname']
    return fullname

async def get_user_action(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]

    documents = await collection.find({}, {"_id": 0}).to_list(None)
    action = documents[0]['action']
    return action


async def get_project_by_id(project_id):
    db = client["Activity"]
    collection = db["Projects"]

    try:
        # Ensure the ID is a valid ObjectId
        obj_id = ObjectId(project_id)
    except Exception as e:
        return {"error": "Invalid project ID format."}

    doc = await collection.find_one({"_id": obj_id})

    if not doc:
        return {"error": "Project not found."}

    project = {
        "_id":"",
        "project_name": doc['project_name'],
        "initiated_date": doc['initiated_date'],
        "due_date": doc['due_date'],
        "team": doc['team'],
        "Status": doc['status'],
        "assigned_member": doc['assigned_members'],
        "project_manager": doc['project_manager'],
        "components": doc['components']
    }

    return project

async def get_task_by_id(task_id):
    db = client["Activity"]
    collection = db["Tasks"]

    try:
        # Ensure the ID is a valid ObjectId
        obj_id = ObjectId(task_id)
    except Exception as e:
        return {"error": "Invalid task ID format."}

    doc = await collection.find_one({"_id": obj_id})

    if not doc:
        return {"error": "task not found."}

# {"_id":"", "task_name":"", "initiated_date":"", "due_date":"", "Status":0 or 1, "assigned_member":[["email", "username"], ["email", "username"]], "desc":"describe of task"}

    task = {
        "_id":"",
        "task_name": doc['task_name'],
        "initiated_date": doc['initiated_date'],
        "due_date": doc['due_date'],
        "Status": doc['status'],
        "assigned_member": doc['assigned_members'],
        "desc":doc['desc']
    }

    return task

async def get_user_projects(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]
    documents = await collection.find({}, {"_id": 0}).to_list(None)
    all_projects = documents[0]['assigned_projects']
    total_projects = len(all_projects)
    done_projects = 0
    project_list = []

    for project in all_projects:
        project_id = list(project.keys())[0]
        project_status = list(project.values())[0]
        project_org = await get_project_by_id(project_id=project_id)
        project_org["_id"] = project_id
        project_org['Status'] = project_status
        if project_org['Status'] == 1:
            done_projects+=1
        project_list.append(project_org)
    
    return project_list, total_projects, done_projects

async def get_user_tasks(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]
    documents = await collection.find({}, {"_id": 0}).to_list(None)
    all_task = documents[0]['assigned_task']
    total_task = len(all_task)
    done_task = 0
    tasks_list = []

    for task in all_task:
        task_id = list(task.keys())[0]
        task_status = list(task.values())[0]
        task_org = await get_task_by_id(task_id=task_id)
        task_org["_id"] = task_id
        task_org['Status'] = task_status
        if task_org['Status'] == 1:
            done_task+=1

        tasks_list.append(task_org)
    
    return tasks_list, total_task, done_task



async def get_client_profile(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]
    documents = await collection.find({}, {"_id": 0}).to_list(None)

    try:
        skills = documents[0]["skills"]
    except KeyError:
        skills = []

    try:
        tnp = documents[0]["tnp"]
    except KeyError:
        tnp = []


    profile = {
        "skills":skills,
        "tnp":tnp,
        "team":documents[0]["team"],
        "email":collection_name
    }

    return profile

async def get_client_notification(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]

    docs = await collection.find({}, {"_id":0}).to_list(None)

    try:
        notifications = docs[0]["notify"]
    except KeyError:
        notifications = []
    
    return notifications[::-1]
    

async def get_total_unread_messages(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]

    docs = await collection.find({}, {"_id":0}).to_list(None)
    unread = 0
    try:
        notifications = docs[0]["notify"]
    except KeyError:
        notifications = []
    
    if notifications:
        for notification in notifications:
            if notification[1] == 0:
                unread+=1
    else:
        return 0
    
    return unread
