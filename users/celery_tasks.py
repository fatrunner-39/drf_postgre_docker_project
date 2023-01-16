from loguru import logger

from celery import shared_task
from send_mail import send_email


@shared_task
def send_email_task(title, message, from_email=None, to_emails=None):
    logger.info('Start email sending')
    send_email(title, message, from_email, to_emails)
    logger.info('Email was send')
