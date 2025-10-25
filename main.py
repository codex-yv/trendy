from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.middleware.cors import CORSMiddleware

from utils.adminPosts import insert_project, insert_task, push_notification_by_admin
from utils.adminGets import get_users, get_projects, get_tasks, get_projet_info, get_task_info, get_users_for_approve, get_all_members, get_admin_notification
from utils.adminPuts import update_user_action, update_project_status_act, update_task_status_act, update_admin_notification

from utils.clientPost import add_new_client, push_notification_by_client, save_unified_chat_message
from utils.clientGets import check_existing_user, check_password, get_username, get_user_action, get_user_projects, get_user_tasks, get_client_profile, get_client_notification, get_project_by_id, get_task_by_id, get_total_unread_messages, get_unified_chat_history
from utils.clientPuts import update_assign_member, update_task_member, update_project_manager, update_project_status_bid, update_task_status_bid, update_user_profile, update_client_notification

from utils.general import create_message, get_users_list, create_message_for_admin
from utils.IST import ISTTime

from schemas.newclientSchemas import NewUser
from schemas.otpSchemas import OTPDetails
from schemas.loginSchemas import LoginSchema
from schemas.adminProjectSchemas import Project
from schemas.adminTasksSchemas import Task
from schemas.useless import Useless, UselessClient
from schemas.adminActionSchemas import AdminAction
from schemas.updatePjtSchemas import UpdateProjets
from schemas.updateTskSchema import UpdateTask
from schemas.profileSchemas import Updated

from datetime import datetime
from typing import Dict, List
import json
import asyncio

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

# Store connected clients
class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections: {user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
        
        # Send current connected users to all clients (optional)
        await self.broadcast_connected_users()
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # print(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
            # Notify remaining users about connection change
            asyncio.create_task(self.broadcast_connected_users())
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def send_notification(self, notification: List, to_users: List[str]):
        """
        Send notification to specific users
        notification format: [message, 0, timestamp]
        """
        message_data = {
            "type": "notification",
            "notification": notification
        }
        
        for user_id in to_users:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message_data))
                    # print(f"Notification sent to {user_id}: {notification[0]}")
                except Exception as e:
                    print(f"Error sending notification to {user_id}: {e}")
                    self.disconnect(user_id)
    
    async def broadcast(self, message: str):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Remove disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_connected_users(self):
        """Broadcast list of connected users to all clients"""
        connected_users = list(self.active_connections.keys())
        message_data = {
            "type": "connected_users",
            "users": connected_users
        }
        await self.broadcast(json.dumps(message_data))
    
    def get_connected_users(self) -> List[str]:
        return list(self.active_connections.keys())

# Create connection manager instance
manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Wait for any message from client (can be used for ping/pong or other commands)
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different types of messages from client
            if message_data.get('type') == 'ping':
                # Respond to ping
                await manager.send_personal_message(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }), user_id)
                
            elif message_data.get('type') == 'test_notification':
                # Echo test notification back to sender
                await manager.send_personal_message(json.dumps({
                    "type": "notification",
                    "notification": message_data.get('notification')
                }), user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

# Unified Community Connection Manager
class UnifiedCommunityConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_info: Dict[str, Dict] = {}  # Store user info like username and type
        
    async def connect(self, websocket: WebSocket, user_id: str, username: str = None, user_type: str = "client"):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_info[user_id] = {
            "username": username or user_id,
            "type": user_type
        }
        
        # Notify all users that someone joined
        await self.broadcast_user_joined(user_id, username)
        # print(f"User {user_id} ({user_type}) joined community chat. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            username = self.user_info[user_id].get("username", user_id)
            user_type = self.user_info[user_id].get("type", "client")
            del self.active_connections[user_id]
            if user_id in self.user_info:
                del self.user_info[user_id]
            
            # Notify all users that someone left
            asyncio.create_task(self.broadcast_user_left(user_id, username))
            # print(f"User {user_id} ({user_type}) left community chat. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_message(self, message_data: dict):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message_data))
            except Exception as e:
                print(f"Error broadcasting to {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Remove disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_user_joined(self, user_id: str, username: str = None):
        message_data = {
            "type": "user_joined",
            "user_id": user_id,
            "username": username or user_id
        }
        await self.broadcast_message(message_data)
    
    async def broadcast_user_left(self, user_id: str, username: str = None):
        message_data = {
            "type": "user_left",
            "user_id": user_id,
            "username": username or user_id
        }
        await self.broadcast_message(message_data)
    
    async def broadcast_chat_message(self, message_data: dict):
        await self.broadcast_message({
            "type": "chat_message",
            "message": message_data
        })
    
    def get_connected_users(self) -> List[str]:
        return list(self.active_connections.keys())

# Create unified community connection manager instance
unified_community_manager = UnifiedCommunityConnectionManager()

# Unified Community WebSocket endpoint for both clients and admins
@app.websocket("/ws/community/{user_id}")
async def unified_community_websocket_endpoint(websocket: WebSocket, user_id: str):
    # Determine if it's an admin or client based on user_id or session
    # For now, we'll check if user_id contains "admin" or use a different method
    user_type = "admin" if "@" not in user_id.lower() else "client"
    
    # Get username from database or use user_id as fallback
    username = "Admin" if user_type == "admin" else user_id
    
    await unified_community_manager.connect(websocket, user_id, username, user_type)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'chat_message':
                # Save message to database
                message_content = message_data.get('message', '').strip()
                if message_content:
                    # Store message in database
                    if username != "Admin":
                        chat_data = {
                            "user": user_id,
                            "username": await get_username(collection_name=user_id),
                            "message": message_content,
                            "time": ISTTime(),
                            "user_type": user_type
                        }
                    else:
                        chat_data = {
                            "user": user_id,
                            "username": username,
                            "message": message_content,
                            "time": ISTTime(),
                            "user_type": user_type
                        }
                    # Save to MongoDB
                    await save_unified_chat_message(chat_data)
                    
                    # Broadcast to ALL users (both clients and admins)
                    await unified_community_manager.broadcast_chat_message(chat_data)
                    
    except WebSocketDisconnect:
        unified_community_manager.disconnect(user_id)
    except Exception as e:
        print(f"Unified Community WebSocket error for user {user_id}: {e}")
        unified_community_manager.disconnect(user_id)




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
        unread = await get_total_unread_messages(collection_name=request.session.get("email"))
        return templates_clients.TemplateResponse("index.html", {"request": request, "fullname": fullname, "details":details, "emailUser":request.session.get("email"), "unreadd": unread})

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

    rmessage = await create_message(message=[project.project_name, "p"])

    await push_notification_by_admin(collections=project.assigned_members, message=rmessage)
    notification = [rmessage, 0, "2023-12-07T10:30:00"]
    to_users = await get_users_list(data = project.assigned_members)
    await manager.send_notification(notification, to_users)

@app.post("/add-task") # FOR ADMIN PAGE.
async def admin_add_tasks(request: Request, task: Task):
    Inserted_id = await insert_task(task=task)
    await update_task_member(collecation_name=task.assigned_members, pid=Inserted_id)
    
    rmessage = await create_message(message=[task.task_name, "t"])

    await push_notification_by_admin(collections=task.assigned_members, message=rmessage)
    notification = [rmessage, 0, "2023-12-07T10:30:00"]
    to_users = await get_users_list(data = task.assigned_members)
    await manager.send_notification(notification, to_users)

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

    fullname = await get_username(collection_name=request.session.get("email"))
    project_name = await get_project_by_id(project_id=data.project_id)

    rmessage = await create_message_for_admin(fullname=fullname, project_taskname=project_name, status=data.status, sym='p')

    await push_notification_by_client(message=rmessage)

    notification = [rmessage, 0, "2023-12-07T10:30:00"]
    to_users = ["qwertyuiop"]
    await manager.send_notification(notification, to_users)




@app.post("/client-tasks")
async def show_client_task(request: Request, x:UselessClient):
    val, total_task, done_task = await get_user_tasks(collection_name=request.session.get("email"))
    # print(val)
    return val


@app.post("/task-checkbox")
async def update_task_status(request: Request, data:UpdateTask):

    await update_task_status_act(pid = data.task_id, status=data.status)
    await update_task_status_bid(task_id = data.task_id, status = data.status, collection_name= request.session.get("email"))

    fullname = await get_username(collection_name=request.session.get("email"))
    taskname = await get_task_by_id(task_id=data.task_id)

    rmessage = await create_message_for_admin(fullname=fullname, project_taskname=taskname, status=data.status, sym='t')

    await push_notification_by_client(message=rmessage)

    notification = [rmessage, 0, "2023-12-07T10:30:00"]
    to_users = ["qwertyuiop"]
    await manager.send_notification(notification, to_users)



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


@app.post("/client-profile")
async def userProfile(request:Request, x:UselessClient):
    details = await get_client_profile(collection_name= request.session.get("email"))
    return details

@app.post("/update-profile")
async def updateProfile(request:Request, data:Updated):
    if data.skills or data.tnp:
        await update_user_profile(collection_name=request.session.get("email"), data=data)
        return 0
    else:
        return 1
    

@app.post("/notification-user")
async def get_notification_user(request:Request, x:UselessClient):
    notifications = await get_client_notification(collection_name=request.session.get("email"))
    await update_client_notification(collection_name=request.session.get("email"))
    return notifications


@app.post("/notification-admin")
async def get_notification_user(request:Request, x:UselessClient):
    notifications = await get_admin_notification()
    await update_admin_notification()
    # print(manager.get_connected_users())
    return notifications

@app.post("/send-notification")
async def senndd(): 
    notification = ["New project assigned to you New project assigned to you", 0, "2023-12-07T10:30:00"]
    to_users = ["qwertyuiop"]
    await manager.send_notification(notification, to_users)
    return 0


# HTTP endpoint to get unified community chats
@app.post("/community")
async def get_unified_community_chats(request: Request):
    try:
        # Get unified chat history from MongoDB
        chats = await get_unified_chat_history()
        return chats
    except Exception as e:
        print(f"Error getting unified community chats: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to load chats"})
    

# HTTP endpoint to send message (works for both clients and admins)
@app.post("/send-message")
async def send_unified_chat_message(request: Request):
    try:
        data = await request.json()
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JSONResponse(status_code=400, content={"error": "Message cannot be empty"})
        
        # Get user info from session or request
        # For demo purposes, we'll use placeholders - replace with actual authentication
        user_id = data.get('user_id', 'unknown_user')
        # username = data.get('username', 'Unknown User')
        # user_type = data.get('user_type', 'client')
        
        if "@" in user_id:
            username = await get_username(collection_name= request.session.get("email"))
            user_type = "client"
        else:
            username = "Admin"
            user_type = "admin"
        # Save message to database
        chat_data = {
            "user": user_id,
            "username": username,
            "message": message_content,
            "time": ISTTime(),
            "user_type": user_type
        }
        
        await save_unified_chat_message(chat_data)
        
        # Broadcast to ALL connected users (both clients and admins)
        await unified_community_manager.broadcast_chat_message(chat_data)
        
        return {"status": "success"}
        
    except Exception as e:
        print(f"Error sending unified message: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to send message"})

