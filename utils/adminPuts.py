from configs.trendyDB import client

async def update_user_action(email:str, action:int):
    db = client["Clients"]
    collection = db[email]

    await collection.update_one(
            {"email": email},
            {"$set": {"action":action}}
        )