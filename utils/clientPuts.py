from configs.trendyDB import client
from bson import ObjectId

async def update_assign_member(collecation_name, pid):
    db = client["Clients"]

    for email in collecation_name:
        collection = db[email[0]]

        await collection.update_one(
            {"email": email[0]},
            {"$push": {"assigned_projects":{str(ObjectId(pid)): 0}}}
        )

async def update_project_manager(collecation_name, pid):
    db = client["Clients"]

    for email in collecation_name:
        collection = db[email[0]]

        await collection.update_one(
            {"email": email[0]},
            {"$push": {"project_manager":str(ObjectId(pid))}}
        )

async def update_task_member(collecation_name, pid):
    db = client["Clients"]

    for email in collecation_name:
        collection = db[email[0]]

        await collection.update_one(
            {"email": email[0]},
            {"$push": {"assigned_task":{str(ObjectId(pid)): 0}}}
        )