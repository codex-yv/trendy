from configs.trendyDB import client
from utils.clientGets import get_project_by_id, get_task_by_id

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

async def get_all_members():
    db = client["Clients"]
    collections_list = await db.list_collection_names()

    members_details = {}

    for collection in collections_list:
        collections = db[collection]

        member_data = await collections.find({}, {"_id": 0}).to_list(None)

        if member_data:

            # test_member_detail = {"name":member_data[0]['fullname'], "team":member_data[0]['team'], "role":member_data[0]['role'], "phone":member_data[0]['phone'], "lastActive":"unknown", "techStack":["Java", "Python"], "assignedProjects":[["Sprite Landing Page", True], ["Trendy webpage", False]], "assignedTask":["Postgrase SQL", "Mysql"]}
            try:
                skills = member_data[0]["skills"]
            except KeyError:
                skills = []
            
            try:
                tnp = member_data[0]["tnp"]
            except KeyError:
                tnp = []
            
            all_skills = skills+tnp

            member_detail = {"name":member_data[0]['fullname'], "team":member_data[0]['team'], "role":member_data[0]['role'], "phone":member_data[0]['phone'], "lastActive":"unknown", "techStack":all_skills, "assignedProjects":[], "assignedTask":[]}

            all_projects = member_data[0]['assigned_projects']
            for project in all_projects:
                project_id = list(project.keys())[0]
                project_org = await get_project_by_id(project_id=project_id)
                if collection == project_org['project_manager'][0][0]:
                    project = [project_org['project_name'], True]
                    member_detail["assignedProjects"].append(project)
                else:
                    project = [project_org['project_name'], False]
                    member_detail["assignedProjects"].append(project)
                
                

            all_task = member_data[0]['assigned_task']
            for task in all_task:
                task_id = list(task.keys())[0]
                task_org = await get_task_by_id(task_id=task_id)
                task_name = task_org['task_name']
                member_detail["assignedTask"].append(task_name)
            
            members_details[member_data[0]['email']] = member_detail

    # print(members_details)
    return members_details


async def get_admin_notification():
    db = client["Admins"]
    collection = db["Base"]

    docs = await collection.find({}, {"_id":0}).to_list(None)

    try:
        notifications = docs[0]["notify"]
    except KeyError:
        notifications = []
    
    return notifications[::-1]