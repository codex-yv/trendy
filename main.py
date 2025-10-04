from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.middleware.cors import CORSMiddleware

from utils.adminPosts import insert_project, insert_task
from utils.adminGets import get_users, get_projects, get_tasks, get_projet_info, get_task_info, get_users_for_approve
from utils.adminPuts import update_user_action

from utils.clientPost import add_new_client
from utils.clientGets import check_existing_user, check_password, get_username
from utils.clientPuts import update_assign_member, update_task_member, update_project_manager

from schemas.newclientSchemas import NewUser
from schemas.otpSchemas import OTPDetails
from schemas.loginSchemas import LoginSchema
from schemas.adminProjectSchemas import Project
from schemas.adminTasksSchemas import Task
from schemas.useless import Useless
from schemas.adminActionSchemas import AdminAction


templates_clients = Jinja2Templates(directory="templates/clients")
templates_admin = Jinja2Templates(directory="templates/admin")


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="qwertyuiopasdfghjkl@#$%RTYU")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
async def home(request:Request):
    return templates_clients.TemplateResponse("login.html", {"request":request})

@app.get("/admin-dashboard")
async def load_admin(request:Request):
    pd, total_projects = await get_projet_info()
    projects = await get_projects()
    recent_projects = projects[0:3]

    td, total_tasks = await get_task_info()
    tasks = await get_tasks()
    recent_tasks = tasks[0:3]

    return templates_admin.TemplateResponse("index.html", {"request":request, "tp":total_projects, "pd":pd, "tt":total_tasks, "td":td, "rp":recent_projects, "rt":recent_tasks})

@app.get("/dashboard")
async def get_dashboard(request: Request):
    try:
        fullname = await get_username(collection_name=request.session.get("email"))
        return templates_clients.TemplateResponse("index.html", {"request": request, "fullname": fullname})

    except TypeError:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)


@app.post("/create-acc")
async def add_new_user(request: Request, data: NewUser = Body(...)):
    request.session["email"] = data.email
    request.session["password"] = data.password

    if not await check_existing_user(collection_name=data.email):
        return JSONResponse(content=0)  # Email already exists

    # Validate OTP
    if "OTP"!= "OTP":  # Replace with real OTP validation
        return JSONResponse(content=1) 

    await add_new_client(client_add=data)
    return RedirectResponse(url="/dashboard", status_code=303)



@app.post("/send-otp")
async def validate_otp(request: Request, data: OTPDetails = Body(...)):
    return 1


@app.post("/make-login")
async def trendy_login(request: Request, data: LoginSchema = Body(...)):

    request.session["email"] = data.email
    request.session["password"] = data.password

    if not await check_existing_user(collection_name=data.email):
        if await check_password(collection_name=data.email, password=data.password):
                 
            return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
        else:
            return 1
    else:
        return 0

@app.post("/add-project")
async def admin_add_projects(request: Request, project: Project):

    # print(project)
    Inserted_id = await insert_project(project=project)
    await update_assign_member(collecation_name=project.assigned_members, pid=Inserted_id)
    await update_project_manager(collecation_name=project.project_manager, pid=Inserted_id)


@app.post("/add-task")
async def admin_add_tasks(request: Request, task: Task):
    Inserted_id = await insert_task(task=task)
    await update_task_member(collecation_name=task.assigned_members, pid=Inserted_id)
    


@app.post("/load-add-project") # FOR ADMIN PAGE.
async def load_add_projects(data:Useless):
    val = await get_users()
    return val
    
@app.post("/load-add-task") # FOR ADMIN PAGE.
async def load_add_projects(data:Useless):
    val = await get_users()
    return val


@app.post("/show-project-status")
async def show_projects(data:Useless):
    val = await get_projects()
    return val

@app.post("/show-task-status")
async def show_task(data:Useless):
    val = await get_tasks()
    return val

@app.post("/approve-signups")
async def show_signup_request(data:Useless):
    user_list = await get_users_for_approve()
    return user_list

@app.post("/action-admin")
async def admin_action(data:AdminAction):

    await update_user_action(email=data.email, action=data.action)