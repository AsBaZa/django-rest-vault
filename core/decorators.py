from rest_framework.response import Response
from rest_framework import status


def check_vault_authorization():
    """ Check authorization using Vault Token """

    def decorator(view_func):
        def _wrapped_view(class_django, request, *args, **kwargs):
            # Get Vault Token metadata
            vault_token_response = request.META.get('VAULT_TOKEN_VALIDATION')

            # If status code is not 200, unauthorized
            if vault_token_response != 200:
                response_text = {'Error 401': 'Invalid Token'}

                return Response(data=response_text, status=status.HTTP_401_UNAUTHORIZED)

            return view_func(class_django, request, *args, **kwargs)
        return _wrapped_view
    return decorator
