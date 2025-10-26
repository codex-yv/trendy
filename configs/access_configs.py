from dotenv import load_dotenv
import os

load_dotenv()

doc_username = os.getenv("DOC_USERNAME")
doc_password = os.getenv("DOC_PASSWORD")
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")