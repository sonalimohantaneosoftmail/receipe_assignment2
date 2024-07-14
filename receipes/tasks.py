# tasks.py

from celery import shared_task
from .models import Notification, User
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_notification(recipient_id, message):
    recipient = User.objects.get(id=recipient_id)
    # sender = User.objects.get(id=sender_id)

    # Create notification
    Notification.objects.create(
        recipient=recipient,
        message=message
    )

    # Send email notification
    send_mail(
        'New Notification',
        message,
        settings.DEFAULT_FROM_EMAIL,  # Use the default from email configured in settings
        [recipient.email],
        fail_silently=False,
    )
