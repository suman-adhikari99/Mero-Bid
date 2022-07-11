from django.urls import path

from .views import *
app_name = "Transactions"
urlpatterns = [

    path("v1/khalti/bid_fee",KhaltiBidFee.as_view()),
    path("v1/khalti/publish_fee",KhaltiPublishFee.as_view()),
    path("v1/esewa/transaction",EsewaTransaction.as_view()),
    path("v1/esewa/bid_fee/success",EsewaBidFeeSuccess.as_view()),
    path("v1/esewa/publish_fee/success",EsewaPublishFeeSuccess.as_view())

]
