import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

config = {
	"sender": "bigalraff@gmail.com",
	"recipients": ["bigalraff@gmail.com"]
}

def send_email(timestamp, dashboard_url):
	body = "AutoARISS started at: " + timestamp + "\nDashboard URL: " + dashboard_url
	msg = MIMEText(body)
	msg["Subject"] = "AutoARISS"
	msg["From"] = config["sender"]
	msg["To"] = ", ".join(config["recipients"])
	with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
		smtp_server.login(config["sender"], os.getenv("GMAIL_APP_PASSWORD"))
		smtp_server.sendmail(config["sender"], config["recipients"], msg.as_string())
