from configs.trendyDB import client
from utils.IST import ISTdate

async def insert_project(project):
    db = client['Activity']
    collection = db['Projects']
    date = f"{ISTdate()}"
    format_data = {
        "project_name":project.project_name,
        "initiated_date":date,
        "due_date":project.due_date,
        "team":project.team,
        "assigned_members":project.assigned_members,
        "project_manager":project.project_manager,
        "components":project.components,
        "status":0
    }

    result = await collection.insert_one(format_data)
    return result.inserted_id


async def insert_task(task):
    db = client['Activity']
    collection = db['Tasks']
    date = f"{ISTdate()}"
    format_data = {
        "task_name": task.task_name,
        "desc": task.desc,
        "initiated_date":date,
        "due_date": task.due_date,
        "assigned_members": task.assigned_members,
        "status":0
    }

    result = await collection.insert_one(format_data)
    return result.inserted_id

