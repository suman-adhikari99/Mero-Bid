from rest_framework.views import APIView
from .models import *
from decorator.auth_decorator import auth_required
from .services.payment_config import  EsewaPaymentVerification
from .services.khalti_payment import  khalti_payment
from Tender.models import TenderBid
from e_bidding.api_render import api_response_render
from django.db import transaction
from constants import PENDING, COMPLETED, ESEWA, WALLET
from decorator.is_publisher import is_publisher
from decorator.is_bidder import is_bidder


class KhaltiBidFee(APIView):  
    @auth_required()
    @is_bidder()
    def post(self, request, user_id ):
        status_msg,status_type ,status_code=khalti_payment(request, user_id ,"Bid",bidder=True)
        return api_response_render(status_msg=status_msg, status_type=status_type, status_code=status_code)
            
            
class KhaltiPublishFee(APIView):  
    @auth_required()
    @is_publisher()
    def post(self, request, user_id ): 
        status_msg,status_type ,status_code= khalti_payment(request, user_id ,"Publish")
        return api_response_render(status_msg=status_msg, status_type=status_type, status_code=status_code)
            

class EsewaTransaction(APIView):

    @auth_required()
    def post(self, request, user_id ): 
        token = request.data.get('token', None)
        amount = request.data.get('amount', None)
        tender_notice_id = request.data.get('tender_notice_id', None)
        tender_bid=TenderBid.objects.filter(user_id=user_id, tender_notice_id=tender_notice_id).last()
        if tender_bid:
            try:
                with transaction.atomic():
                    TransactionMain.store_transaction_main(ESEWA,tender_notice_id,tender_bid.user,amount,WALLET,token,PENDING,"Bid")
                    return api_response_render(status_msg="Payment Initiated", status_type='Success',status_code=200)
            except Exception as e:
                    return api_response_render(status_msg=str(e), status_type='Error', status_code=500)      
        return api_response_render(status_msg="Tender Bid Doesn't Exist", status_type='Error', status_code=400)



class EsewaBidFeeSuccess(APIView):
    @auth_required()
    @is_bidder()
    def post(self,request,user_id):
        try:
            idx = request.data.get("oid")
            transaction_main=TransactionMain.objects.filter (transaction_idx=idx,user_id=user_id,status=PENDING).last()
            tender_bid=TenderBid.objects.filter(user_id=user_id, tender_notice_id=transaction_main.tender_notice_id).last()
            response=EsewaPaymentVerification(request)
            if response.status_code==200:
                if transaction_main:
                    transaction_main.status=COMPLETED
                    transaction_main.save()
                    tender_bid.epayment_status()
                    TransactionDetail.store_transaction_detail(transaction_main.status,transaction_main)
                    return api_response_render(status_msg="Payment Successfull", status_type='Success',status_code=200)
                return api_response_render(status_msg="Transaction Doesn't Exist", status_type='Error',status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

        

class EsewaPublishFeeSuccess(APIView):
    @auth_required()
    @is_publisher()
    def post(self,request,user_id):
        try:
            tender_notice_id=request.data.get("tender_notice_id")
            tender_notice=TenderNotice.objects.filter(id=tender_notice_id,user_id=user_id).last()
            response=EsewaPaymentVerification(request)
            if response.status_code==200:
                if tender_notice:
                    tender_notice.deposit_paid=True
                    tender_notice.save()
                    TransactionMain.store_transaction_main(ESEWA,tender_notice_id,tender_notice.user,request.data.get("amt"),WALLET,request.data.get("oid"),COMPLETED,"Publish")
                    return api_response_render(status_msg="Payment Successfull", status_type='Success',status_code=200)
                return api_response_render(status_msg="Tender Notice Doesn't Exist", status_type='Error',status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

        



