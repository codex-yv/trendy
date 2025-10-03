from configs.trendyDB import client

async def get_users():
    db = client["Clients"]
    colls = await db.list_collection_names()  # FIXED

    users_dict = {}

    for coll in colls:
        collection = db[coll]

        user_data = await collection.find({}, {"_id": 0}).to_list(None)

        if user_data:
            user_desc = user_data[0]['fullname'] + " - " + user_data[0]['team']
            users_dict[coll] = user_desc

    return users_dict