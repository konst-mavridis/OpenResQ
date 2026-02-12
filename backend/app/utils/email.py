# app/email_utils.py
import smtplib
from email.mime.text import MIMEText

SMTP_USER = "bikethe200.dev@gmail.com"
SMTP_PASS = "njze sqbd vnif kmtj"

def send_reset_email(to_email: str, reset_link: str):
    html = f"""
    <div style="font-family:Arial;padding:20px">
      <h2 style="color:#d32f2f">OpenResQ Password Reset</h2>
      <p>You requested a password reset.</p>
      <p>Click the button below:</p>
      <a href="{reset_link}"
         style="background:#d32f2f;color:white;padding:10px 20px;
                text-decoration:none;border-radius:6px;">
         Reset Password
      </a>
      <p>This link expires in 1 hour.</p>
    </div>
    """

    msg = MIMEText(html, "html")
    msg["Subject"] = "OpenResQ Password Reset"
    msg["From"] = f"OpenResQ <{SMTP_USER}>"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

def send_email(to_email: str, subject: str, html: str):
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = f"OpenResQ <{SMTP_USER}>"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
