from rest_framework.serializers import ModelSerializer

from .models import Assessment


class AssessmentSerializer(ModelSerializer):
    class Meta:
        model = Assessment