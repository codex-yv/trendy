from configs.trendyDB import client
from bson import ObjectId
from utils.adminGets import get_admin_notification
from utils.general import is_completed_project

async def update_user_action(email:str, action:int):
    db = client["Clients"]
    collection = db[email]
    # action {-1:Pending, 0:Rejected, 1:Approved}
    await collection.update_one(
            {"email": email},
            {"$set": {"action":action}}
        )
    

async def update_project_status_act(pid, status:int, username:str):
    db = client["Activity"]
    collection = db["Projects"]
    obj_id = ObjectId(pid)

    assigned_members = await collection.find_one(
        {"_id":obj_id},
        {"assigned_members":1, "_id":0}
    ) # /getting assigned members of a given project.

    updated_assigned_members = [] # it will contain the updated list of members who has marked the project as completed (1) and those who are still doing it(0).

    for member in assigned_members.get("assigned_members"):
        if member[0] == username:
            try:
                member[2] = status
            except IndexError:
                member.append(status)
        updated_assigned_members.append(member)

    project_status = await is_completed_project(members=updated_assigned_members) # when all members has completed the project it will return one else 0.

    await collection.update_one(
            {"_id": obj_id},
            {"$set": {"status":project_status,
                      "assigned_members":updated_assigned_members}}
        )
    
async def update_task_status_act(pid, status:int, username:str):
    db = client["Activity"]
    collection = db["Tasks"]
    obj_id = ObjectId(pid)

    assigned_members = await collection.find_one(
        {"_id":obj_id},
        {"assigned_members":1, "_id":0}
    ) # /getting assigned members of a given task.

    updated_assigned_members = [] # it will contain the updated list of members who has marked the project as completed (1) and those who are still doing it(0).

    for member in assigned_members.get("assigned_members"):
        if member[0] == username:
            try:
                member[2] = status
            except IndexError:
                member.append(status)
        updated_assigned_members.append(member)

    task_status = await is_completed_project(members=updated_assigned_members) # when all members has completed the task it will return 1 else 0.
    await collection.update_one(
            {"_id": obj_id},
            {"$set": {"status":task_status,
                      "assigned_members":updated_assigned_members}}
        )
    
async def update_admin_notification():
    db = client["Admins"]
    collection = db["Base"]

    notifications = await get_admin_notification()

    new_notification = []
    for notification in notifications[::-1]:
        if notification[1] != 1:
            notification[1] = 1

        new_notification.append(notification)
    
    # print (new_notification)
    await collection.update_one(
        {"unique":"qwertyuiop"},
        {"$set":{"notify":new_notification}}
    )

async def delete_project_by_id(project_id:str):
    db = client["Activity"]
    collection = db["Projects"]
    db2 = client["Clients"]
    project_data = await collection.find_one({"_id":ObjectId(project_id)})
    assigned_data = project_data.get("assigned_members")
    project_title = project_data.get("project_name")
    for member in assigned_data:
        collection2 = db2[member[0]]
        assigned_projects = (await collection2.find({},{"_id":0}).to_list(None))[0]["assigned_projects"]
        new_assigned_members = []
        for project in assigned_projects:
            if project_id not in project:
                new_assigned_members.append(project)

        await collection2.update_one(
                    {"email":member[0]},
                    {"$set":{"assigned_projects":new_assigned_members}}
                )
    
    await collection.delete_one({"_id":ObjectId(project_id)})
    return assigned_data, project_title

async def delete_task_by_id(task_id:str):
    db = client["Activity"]
    collection = db["Tasks"]
    db2 = client["Clients"]
    task_data = await collection.find_one({"_id":ObjectId(task_id)})
    assigned_data = task_data.get("assigned_members")
    task_title = task_data.get("task_name")
    for member in assigned_data:
        collection2 = db2[member[0]]
        assigned_task = (await collection2.find({},{"_id":0}).to_list(None))[0]["assigned_task"]
        new_assigned_members = []
        for task in assigned_task:
            if task_id not in task:
                new_assigned_members.append(task)

        await collection2.update_one(
                    {"email":member[0]},
                    {"$set":{"assigned_task":new_assigned_members}}
                )
    
    await collection.delete_one({"_id":ObjectId(task_id)})
    return assigned_data, task_title