from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.plots.models import Plot
from .engine import get_recommendations


class RecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, plot_id):
        plot = get_object_or_404(Plot, id=plot_id, owner=request.user)
        cards = get_recommendations(plot)
        return Response(cards)
