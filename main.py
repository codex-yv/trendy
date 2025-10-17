from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.middleware.cors import CORSMiddleware

from utils.adminPosts import insert_project, insert_task
from utils.adminGets import get_users, get_projects, get_tasks, get_projet_info, get_task_info, get_users_for_approve, get_all_members
from utils.adminPuts import update_user_action, update_project_status_act, update_task_status_act

from utils.clientPost import add_new_client
from utils.clientGets import check_existing_user, check_password, get_username, get_user_action, get_user_projects, get_user_tasks
from utils.clientPuts import update_assign_member, update_task_member, update_project_manager, update_project_status_bid, update_task_status_bid

from schemas.newclientSchemas import NewUser
from schemas.otpSchemas import OTPDetails
from schemas.loginSchemas import LoginSchema
from schemas.adminProjectSchemas import Project
from schemas.adminTasksSchemas import Task
from schemas.useless import Useless, UselessClient
from schemas.adminActionSchemas import AdminAction
from schemas.updatePjtSchemas import UpdateProjets
from schemas.updateTskSchema import UpdateTask

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

@app.get("/login") # FOR Client PAGE.
async def home(request:Request):
    return templates_clients.TemplateResponse("login.html", {"request":request})

@app.get("/admin-dashboard") # FOR ADMIN PAGE.
async def load_admin(request:Request):
    pd, total_projects = await get_projet_info()
    projects = await get_projects()
    recent_projects = projects[0:3]

    td, total_tasks = await get_task_info()
    tasks = await get_tasks()
    recent_tasks = tasks[0:3]

    return templates_admin.TemplateResponse("index.html", {"request":request, "tp":total_projects, "pd":pd, "tt":total_tasks, "td":td, "rp":recent_projects, "rt":recent_tasks})

@app.get("/rejected")
async def display_rejected_page(request: Request):
    fullname = await get_username(collection_name=request.session.get("email"))
    return templates_clients.TemplateResponse("rejected.html", {"request": request, "fullname": fullname})

@app.get("/pending")
async def display_pending_page(request: Request):

    fullname = await get_username(collection_name=request.session.get("email"))
    return templates_clients.TemplateResponse("pending.html", {"request": request, "fullname": fullname})


@app.get("/dashboard") # FOR Client PAGE.
async def get_dashboard(request: Request):
    try:
        fullname = await get_username(collection_name=request.session.get("email"))
        tasks, total_task, done_task = await get_user_tasks(collection_name=request.session.get("email"))
        projects, total_projects, done_projects = await get_user_projects(collection_name=request.session.get("email"))
        details = {
            "total assigned projects": total_projects,          
            "completed projects": done_projects,               
            "total assigned tasks": total_task,             
            "completed tasks": done_task,                  
            "recent projects": projects,                
            "recent tasks": tasks                    
        }
        # print(projects)
        return templates_clients.TemplateResponse("index.html", {"request": request, "fullname": fullname, "details":details})

    except TypeError:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

@app.get("/success")
async def sign_up_success(request: Request):
    return templates_clients.TemplateResponse("success.html", {"request": request})


@app.post("/create-acc") # FOR Client PAGE.
async def add_new_user(request: Request, data: NewUser = Body(...)):
    request.session["email"] = data.email
    request.session["password"] = data.password

    if not await check_existing_user(collection_name=data.email):
        return JSONResponse(content=0)  # Email already exists

    # Validate OTP
    if "OTP"!= "OTP":  # Replace with real OTP validation
        return JSONResponse(content=1) 

    await add_new_client(client_add=data)
    return RedirectResponse(url="/success", status_code=303)



@app.post("/send-otp") # FOR Client PAGE.
async def validate_otp(request: Request, data: OTPDetails = Body(...)):
    return 1


@app.post("/make-login") # FOR Client PAGE.
async def trendy_login(request: Request, data: LoginSchema = Body(...)):

    request.session["email"] = data.email
    request.session["password"] = data.password

    if not await check_existing_user(collection_name=data.email):
        if await check_password(collection_name=data.email, password=data.password):
            action = await get_user_action(collection_name=data.email)

            if action == 0:
                return RedirectResponse(url="/rejected", status_code=HTTP_303_SEE_OTHER)
            elif action == -1:
                return RedirectResponse(url="/pending", status_code=HTTP_303_SEE_OTHER)
            else:        
                return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
        else:
            return 1
    else:
        return 0

@app.post("/add-project") # FOR ADMIN PAGE.
async def admin_add_projects(request: Request, project: Project):

    # print(project)
    Inserted_id = await insert_project(project=project)
    await update_assign_member(collecation_name=project.assigned_members, pid=Inserted_id)
    await update_project_manager(collecation_name=project.project_manager, pid=Inserted_id)


@app.post("/add-task") # FOR ADMIN PAGE.
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


@app.post("/show-project-status") # FOR ADMIN PAGE.
async def show_projects(data:Useless):
    val = await get_projects()
    return val

@app.post("/show-task-status") # FOR ADMIN PAGE.
async def show_task(data:Useless):
    val = await get_tasks()
    return val

@app.post("/approve-signups") # FOR ADMIN PAGE.
async def show_signup_request(data:Useless):
    user_list = await get_users_for_approve()
    return user_list

@app.post("/action-admin") # FOR ADMIN PAGE.
async def admin_action(data:AdminAction):

    await update_user_action(email=data.email, action=data.action)


@app.post("/client-projects")
async def show_client_projects(request: Request, x:UselessClient):
    val, total_projects, done_projects = await get_user_projects(collection_name=request.session.get("email"))
    return val

@app.post("/project-checkbox")
async def update_project_status(request: Request,data: UpdateProjets):

    await update_project_status_act(pid=data.project_id, status=data.status)
    await update_project_status_bid(project_id=data.project_id, status=data.status, collection_name=request.session.get("email"))

@app.post("/client-tasks")
async def show_client_task(request: Request, x:UselessClient):
    val, total_task, done_task = await get_user_tasks(collection_name=request.session.get("email"))
    print(val)
    return val


@app.post("/task-checkbox")
async def update_task_status(request: Request, data:UpdateTask):

    await update_task_status_act(pid = data.task_id, status=data.status)
    await update_task_status_bid(task_id = data.task_id, status = data.status, collection_name= request.session.get("email"))

@app.post("/client-dashboard")
async def update_dashboard_fapi(request: Request, x:UselessClient):
    tasks, total_task, done_task = await get_user_tasks(collection_name=request.session.get("email"))
    projects, total_projects, done_projects = await get_user_projects(collection_name=request.session.get("email"))
    details = {
        "total assigned projects": total_projects,          
        "completed projects": done_projects,               
        "total assigned tasks": total_task,             
        "completed tasks": done_task,                  
        "recent projects": projects,                
        "recent tasks": tasks                    
    }
    return details


@app.post("/mps")
async def show_members(request:Request, x:Useless):
    return_value = await get_all_members()
    # print(return_value)
    return return_value