from configs.trendyDB import client
from bson import ObjectId
from utils.adminGets import get_admin_notification


async def update_user_action(email:str, action:int):
    db = client["Clients"]
    collection = db[email]
    # action {-1:Pending, 0:Rejected, 1:Approved}
    await collection.update_one(
            {"email": email},
            {"$set": {"action":action}}
        )
    

async def update_project_status_act(pid, status:int):
    db = client["Activity"]
    collection = db["Projects"]
    obj_id = ObjectId(pid)
    await collection.update_one(
            {"_id": obj_id},
            {"$set": {"status":status}}
        )
    
async def update_task_status_act(pid, status:int):
    db = client["Activity"]
    collection = db["Tasks"]
    obj_id = ObjectId(pid)
    await collection.update_one(
            {"_id": obj_id},
            {"$set": {"status":status}}
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