from configs.trendyDB import client
from bson import ObjectId
from utils.clientGets import get_client_notification


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


async def update_project_status_bid(project_id, status, collection_name):
    db = client["Clients"]
    collection = db[collection_name]
    document_filter={"email": collection_name}

    key = f"assigned_projects.$.{project_id}"

    await collection.update_one(
        {**document_filter, f"assigned_projects.{project_id}": {"$exists": True}},
        {"$set": {key: status}}
    )

async def update_task_status_bid(task_id, status, collection_name):
    db = client["Clients"]
    collection = db[collection_name]
    document_filter={"email": collection_name}

    key = f"assigned_task.$.{task_id}"

    await collection.update_one(
        {**document_filter, f"assigned_task.{task_id}": {"$exists": True}},
        {"$set": {key: status}}
    )

async def update_user_profile(collection_name:str, data:object):
    db = client["Clients"]
    collection = db[collection_name]

    if data.skills:
        await collection.update_one(
            {"email":collection_name},
            {"$set":{"skills":data.skills}}
        )
    elif data.tnp:
        await collection.update_one(
            {"email":collection_name},
            {"$set":{"tnp":data.tnp}}
        )

async def update_client_notification(collection_name:str):
    db = client["Clients"]
    collection = db[collection_name]

    notifications = await get_client_notification(collection_name=collection_name)

    new_notification = []
    for notification in notifications[::-1]:
        if notification[1] != 1:
            notification[1] = 1

        new_notification.append(notification)
    
    # print (new_notification)
    await collection.update_one(
        {"email":collection_name},
        {"$set":{"notify":new_notification}}
    )

        



    
    