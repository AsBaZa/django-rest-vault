import requests
from django.conf import settings


def check_vault_token(sender, environ, **kwargs):
    _ = kwargs
    _ = sender

    # Get Token sent on header `X-Vault-Token`
    x_vault_token = environ.get('HTTP_X_VAULT_TOKEN')

    if x_vault_token:
        # Check Token validation
        r = requests.get(settings.VAULT_TOKEN_LOOKUP_SELF,
                         headers={'X-Vault-Token': x_vault_token})

        # Save the response of Vault using the environ variable `VAULT_TOKEN_RESPONSE`
        environ['VAULT_TOKEN_VALIDATION'] = r.status_code
