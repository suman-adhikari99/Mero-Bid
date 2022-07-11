from rest_framework import serializers

from .models import *


class TestimonialsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Testimonals
        fields='__all__'

class ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Clients
        fields='__all__'

