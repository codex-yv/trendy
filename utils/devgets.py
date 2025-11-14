from configs.trendyDB import client

async def get_total_users():
    db = client["Clients"]
    collection = await db.list_collection_names()
    total_users = len(collection)
    return total_users


async def push_notification_by_dev(collections:list[str], message:str):

    db = client["Clients"]
    aMessage = [message, 0]

    for collection_name in collections:
        collection = db[collection_name]

        await collection.update_one(
            {"email":collection_name},
            {"$push": {"notify": aMessage}}
        )
    
    db2 = client["Admins"]
    collection2 = db2["Base"]

    await collection2.update_one(
            {"unique":"qwertyuiop"},
            {"$push": {"notify": aMessage}}
        )