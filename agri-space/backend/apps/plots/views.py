from rest_framework.response import Response
from rest_framework.views import APIView


class PlotListView(APIView):
    """Stub view — full implementation in Backend Task 4."""

    def get(self, request):
        return Response([])
