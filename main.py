from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.middleware.cors import CORSMiddleware
from utils.clientPost import add_new_client
from utils.clientGets import check_existing_user, check_password, get_username
from schemas.newclientSchemas import NewUser
from schemas.otpSchemas import OTPDetails
from schemas.loginSchemas import LoginSchema

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
