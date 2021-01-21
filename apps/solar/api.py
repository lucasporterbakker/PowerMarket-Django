from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from .calculations import (
    environmental_benefits_serialized,
    get_fit_rate,
)
from .models import Assessment
from .serializers import *


class EnvironmentalBenefitsAPIView(APIView):
    """
    Returns environmental benefits equivalent for a given amount of energy.
    """
    def get(self, **kwargs):
        energy = kwargs.get('energy')
        try:
            energy = float(energy)
        except ValueError:
            energy = None
        if not energy:
            return Response(
                {"Message": _("Energy missing in **kwargs.")},
                status=404,
            )
        else:
            return Response(
                environmental_benefits_serialized(energy),
                status=200
            )


class FitRateAPIView(APIView):
    def get(self, *args, **kwargs):
        annual_energy = float(kwargs.get('annual_energy'))
        target_date_str = kwargs.get('target_date')
        if target_date_str:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        else:
            target_date = datetime.now().date()
        fit_rate = get_fit_rate(annual_energy, target_date=target_date)
        return Response(
            {
                "annual_energy": annual_energy,
                "target_date": target_date,
                "fit_rate": fit_rate,
            },
            status=200,
        )


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
