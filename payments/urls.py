from django.urls import path
from . import webhooks


urlpatterns = [
    path('webhook/', webhooks.liqpay_webhook, name='liqpay-webhook'),
]