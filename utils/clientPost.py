from configs.trendyDB import client
from security.encryptPass import encryptt

async def add_new_client(client_add:dict):
    db = client["Clients"]
    collection = db[client_add.email]
    key, token = encryptt(password=client_add.password)
    format_data = {
        "fullname":client_add.fullName,
        "email":client_add.email,
        "phone":client_add.phone,
        "password":token,
        "key":key,
        "status":"ACTIVE",
        "profileImg":"",
        "team":"",
        "role":client_add.role,
        "assigned_projects":[],  # total projects done
        "assigned_task":[],    # pending projects
        "project_manager":[],
        "notifications":[],     # ongoing projects
        "techstack":{}
    }

    await collection.insert_one(format_data)