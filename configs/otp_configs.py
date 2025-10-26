from dotenv import load_dotenv
import os

load_dotenv()

sender_email = os.getenv("EMAIL")
sender_key = os.getenv("SENDGRID_API_KEY")