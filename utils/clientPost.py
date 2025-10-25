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
        "team":client_add.team,
        "role":client_add.role,
        "skills":client_add.skills,
        "tnp":client_add.tnp,
        "assigned_projects":[],  # total projects done
        "assigned_task":[],    # pending projects
        "project_manager":[],
        "notifications":[],     # ongoing projects
        "techstack":{},
        "action":-1
    }

    await collection.insert_one(format_data)


async def push_notification_by_client(message:str):

    db = client["Admins"]
    collection = db["Base"]

    aMessage = [message, 0]
    
    await collection.update_one(
        {"unique":"qwertyuiop"},
        {"$push": {"notify": aMessage}}
    )


async def save_unified_chat_message(chat_data: dict):
    """
    Save chat message to database
    Replace this with your actual database implementation
    """
    db = client["History"]
    collection = db["chat"]

    format_chat = {
        'user':chat_data['user'],
        'username':chat_data['username'],
        'message':chat_data['message'],
        'time':chat_data['time'], 
        'user_type':chat_data['user_type']
    }

    await collection.insert_one(format_chat)