from configs.trendyDB import client

async def insert_project(project):
    db = client['Activity']
    collection = db['Projects']

    format_data = {
        "project_name":project.project_name,
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

    format_data = {
        "task_name": task.task_name,
        "desc": task.desc,
        "due_date": task.due_date,
        "assigned_members": task.assigned_members,
        "status":0
    }

    result = await collection.insert_one(format_data)
    return result.inserted_id