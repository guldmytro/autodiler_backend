from rest_framework_simplejwt.tokens import Token
from datetime import timedelta


class MagicLinkToken(Token):
    token_type = 'magic'
    lifetime = timedelta(minutes=15)