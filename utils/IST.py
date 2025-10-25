from datetime import datetime
import pytz

def ISTdate():
    ist = pytz.timezone('Asia/Kolkata')
    ist_date = datetime.now(ist)
    return ist_date.strftime("%d/%m/%Y")

def ISTTime():
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.now(ist)
    return ist_time.strftime("%I:%M %p")