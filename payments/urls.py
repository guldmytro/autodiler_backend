from django.urls import path
from . import webhooks


urlpatterns = [
    path('webhook/', webhooks.liqpay_webhook, name='liqpay-webhook'),
    path('webhook-mono/', webhooks.monobank_webhook, name='monobank-webhook'),
]