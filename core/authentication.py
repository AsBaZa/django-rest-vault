from django.contrib.auth.models import User
from rest_framework import authentication
from django.conf import settings
import requests


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        x_vault_token = request.META.get('HTTP_X_VAULT_TOKEN')

        if x_vault_token:
            # Check Token validation
            r = requests.get(settings.VAULT_TOKEN_LOOKUP_SELF, headers={'X-Vault-Token': x_vault_token})

            if r.status_code == 200:
                username = r.json()['data']['meta']['username']
                return [User(username=username), None]
        return None
