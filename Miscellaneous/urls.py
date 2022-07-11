
from django.urls import path

from Miscellaneous.views import *
app_name="miscellaneous"
urlpatterns=[
    path('v1/testimonials',TestimonialView.as_view()),
    path('v1/our-clients', ClientView.as_view()),
    ]