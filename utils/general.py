from utils.IST import ISTdate, ISTTime
from utils.clientGets import get_client_password
import random
from configs.otp_configs import sender_email, sender_key
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


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

async def generate_otp():
    otp = random.randint(100000, 999999)
    return otp

async def send_otp(email: str):
    otp = await generate_otp()

    message = Mail(
        from_email=sender_email,  # must be verified in SendGrid
        to_emails=email,
        subject="Your OTP Code",
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
            <div style="max-width:500px; margin:auto; background:#ffffff; padding:20px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h2 style="color:#333; text-align:center;">✨ Trendy Member's Portal Verification</h2>
                <p style="color:#444; font-size:15px;">Hi there,</p>
                <p style="color:#444; font-size:15px;">
                    Your one-time password (OTP) to <b>sign up at Trendy Member's Portal</b> is:
                </p>
                <div style="text-align:center; margin:20px 0;">
                    <span style="display:inline-block; font-size:24px; font-weight:bold; letter-spacing:4px; color:#e91e63; padding:10px 20px; border:2px dashed #e91e63; border-radius:6px;">
                        {otp}
                    </span>
                </div>
                <p style="color:#444; font-size:15px;">
                    ⏳ This code is valid for <b>5 minutes</b>. Please do not share it with anyone for your account’s safety.
                </p>
                <p style="color:#444; font-size:15px; margin-top:30px;">
                    Thanks,<br>
                    <b>Trendy Team</b>
                </p>
                <hr style="margin:20px 0; border:none; border-top:1px solid #eee;">
                <p style="font-size:12px; color:#888; text-align:center;">
                    If you didn’t request this code, you can safely ignore this email.
                </p>
            </div>
        </body>
        </html>
        """


            )

    try:
        sg = SendGridAPIClient(sender_key)
        sg.send(message)
        return otp
    except Exception as e:
        print(f"Error sending email: {e}")
        return None
    
async def send_password(email: str):
    password = await get_client_password(collection_name=email)

    message = Mail(
        from_email=sender_email,  # must be verified in SendGrid
        to_emails=email,
        subject="Your password for Trendy member portal login.",
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
            <div style="max-width:500px; margin:auto; background:#ffffff; padding:20px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                <h2 style="color:#333; text-align:center;">🔑 Trendy Member's Portal Login Details</h2>
                <p style="color:#444; font-size:15px;">Hi there,</p>
                <p style="color:#444; font-size:15px;">
                    Your password to <b>log in to Trendy Member's Portal</b> is:
                </p>
                <div style="text-align:center; margin:20px 0;">
                    <span style="display:inline-block; font-size:24px; font-weight:bold; letter-spacing:2px; color:#e91e63; padding:10px 20px; border:2px dashed #e91e63; border-radius:6px;">
                        {password}
                    </span>
                </div>
                <p style="color:#444; font-size:15px;">
                    🔒 Please keep this password confidential and do not share it with anyone.
                </p>
                <p style="color:#444; font-size:15px; margin-top:30px;">
                    Thanks,<br>
                    <b>Trendy Team</b>
                </p>
                <hr style="margin:20px 0; border:none; border-top:1px solid #eee;">
                <p style="font-size:12px; color:#888; text-align:center;">
                    If you didn’t request this password, please contact our support team immediately.
                </p>
            </div>
        </body>
        </html>
        """



            )

    try:
        sg = SendGridAPIClient(sender_key)
        sg.send(message)
        return 1
    except Exception as e:
        print(f"Error sending email: {e}")
        return 2