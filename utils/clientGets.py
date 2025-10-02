from configs.trendyDB import client
from security.decryptPass import decryptt

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
