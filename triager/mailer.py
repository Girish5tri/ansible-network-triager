import logging
import smtplib
from datetime import date
from email.message import EmailMessage
from triager.ci_report import generate_ci_report

def send_mail(content, config, subject):
    logging.info("attempting to send email to maintainers") 
    msg = EmailMessage()
    msg["From"] = config.sender["email"]
    msg["To"] = config.maintainers
    msg["Subject"] = subject

    msg.set_content(str(content))
    msg.add_alternative(
        content.get_html_string(
            attributes={"border": "1", "style": "text-align:center"}
        ),
        subtype="html",
    )
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            logging.info("attempting to send email")
            smtp.starttls()
            smtp.login(config.sender["email"], config.sender["password"])
            smtp.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def send_bug_report(content, config):
    subject = f"Ansible Network Weekly Triage - Bug Report - {date.today().isoformat()}"
    send_mail(content, config, subject)

def send_ci_report(content, config):
    ci_report = generate_ci_report(config)
    status = ci_report.get("overall_status", "Unknown")
    report_date = ci_report.get("date", date.today().isoformat())
    
    subject = f"Ansible Network Nightly CI Report - {report_date} - {status}"
    send_mail(content, config, subject)

