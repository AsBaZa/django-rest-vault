from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class HelloWorldView(APIView):
    """
    # Hello World
    """

    def get(self, request):
        _ = request

        return Response({"Hello": "World"})
