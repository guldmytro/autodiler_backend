from djoser import email
from django.conf import settings


class ActivationEmail(email.ActivationEmail):
    template_name = 'email/my_activation.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['frontend_url'] = settings.CORS_ALLOWED_ORIGINS[-1]
        return context

    def get_subject(self):
        return 'Активація користувача'