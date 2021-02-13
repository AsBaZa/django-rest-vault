from rest_framework.response import Response
from rest_framework.views import APIView
from .decorators import check_vault_authorization


# Create your views here.
class HelloWorldView(APIView):
    """
    # Hello World
    """

    @check_vault_authorization()
    def get(self, request):
        _ = request

        # Response text
        text = {'Hello': 'World!'}

        return Response(text)
