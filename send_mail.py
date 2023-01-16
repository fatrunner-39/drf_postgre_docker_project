import os

from django.conf import settings
from django.core.mail import EmailMessage


def send_email(title, message, from_email=settings.EMAIL_HOST_USER, to_emails=None):
    if type(to_emails) != list:
        to_emails = [to_emails]
    email = EmailMessage(
        title,
        message,
        from_email,
        to_emails
    )
    email.send()


def user_greeting(full_name):
    return f'Hello {full_name}! You are welcome to our app!'
