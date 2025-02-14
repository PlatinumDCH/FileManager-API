from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import smtplib

from backend.app.core.config import settings

templates_dir = '/frontend/templates'
env = Environment(loader=FileSystemLoader(templates_dir))

def render_template(template_name, **context):
    '''rendering html-temolate'''
    template = env.get_template(template_name)
    return template.render(**context)

def send_email(to_email, subject, html_content):
    '''send email SMTP'''
    msg = MIMEMultipart()
    msg.add_header('Return-Path', settings.MAIL_USERNAME)
    msg['From'] = settings.MAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f'SMTP error; {str(e)}')