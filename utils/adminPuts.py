from configs.trendyDB import client
from bson import ObjectId

async def update_user_action(email:str, action:int):
    db = client["Clients"]
    collection = db[email]

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