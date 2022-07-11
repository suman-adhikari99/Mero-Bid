from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from . serializers import *

from .models import *
# Create your views here.

class TestimonialView(APIView):
    #permission_classes = (IsAuthenticated,)
    def get(self,request):
        testimonilas=Testimonals.objects.all()
        serialized_testimonials=TestimonialsSerializer(testimonilas,many=True)
        return Response(data=serialized_testimonials.data,status=status.HTTP_200_OK)


class ClientView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self,request):
        clients = Clients.objects.all()
        serialized_client=ClientsSerializer(clients,many=True)
        return Response(data=serialized_client.data, status=status.HTTP_200_OK)

