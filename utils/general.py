from utils.IST import ISTdate, ISTTime
async def create_message(message:list[str, str]):
    
    """
    message = ["project or task name", "p - if project or t - if task"]
    """
    if message[1] == 'p':
        rMessage = f"Project '{message[0].title()}' is assigned to you on {ISTdate()} at {ISTTime()}"
    else:
        rMessage = f"Task '{message[0].title()}' is assigned to you on {ISTdate()} at {ISTTime()}"

    return rMessage


async def get_users_list(data):
    users = []
    for user in data:
        users.append(user[0])
    return users


async def create_message_for_admin(fullname:str, project_taskname:str, status:int, sym:str):
    '''
    message = [project/task name, username, t/p, s]
    '''

    if sym == 'p':
        if status == 1:
            rMessage = f"{fullname} has MARKED the project '{project_taskname['project_name']}' for completed on {ISTdate()} at {ISTTime()}!"
        else:
            rMessage = f"{fullname} has UNMARKED the project '{project_taskname['project_name']}' for Incomplete on {ISTdate()} at {ISTTime()}!"
    else:
        if status == 1:
            rMessage = f"{fullname} has MARKED the task '{project_taskname['task_name']}' for completed on {ISTdate()} at {ISTTime()}!"
        else:
            rMessage = f"{fullname} has UNMARKED the task '{project_taskname['task_name']}' for Incomplete on {ISTdate()} at {ISTTime()}!"

    return rMessage