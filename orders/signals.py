from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.template.loader import render_to_string
from django.conf import settings
from api.telegram import send_telegram_message


@receiver(post_save, sender=Order)
def create_profile(sender, instance, created, **kwargs):
    if created:
        base_url = settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) > 0 else '127.0.0.1:8000'
        message = render_to_string('emails/new-order.html', {
            'order': instance,
            'base_url': base_url
        })
        subject = 'Нове замовлення'
        to = settings.EMAIL_RECEPIENTS
        send_telegram_message(message)
