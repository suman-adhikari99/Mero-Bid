from ..models import TransactionMain, TransactionDetail
from Tender.models import TenderBid, TenderNotice
from .payment_config import KhaltiPaymentVerification
from django.db import transaction
from constants import KHALTI


def khalti_payment(request, user_id ,fee_for, bidder=False):
   token = request.data.get('token', None)
   amount = request.data.get('amount', None)
   response = KhaltiPaymentVerification(amount, token)
   tender_notice_id = request.data.get('tender_notice_id', None)
   if response.status_code==200:
       try:
           with transaction.atomic():
              data=response.json()  
              amount =data.get('amount')/100
              status=data['state']['name']
              payment_type=data['type']['name']
              idx=data['idx']                    
              if bidder:
                   tender_bid=TenderBid.objects.filter(user_id=user_id, tender_notice_id=tender_notice_id).last()
                   if tender_bid:
                       transaction_main=TransactionMain.store_transaction_main(KHALTI,tender_notice_id,tender_bid.user,amount,payment_type,idx,status,fee_for)
                       TransactionDetail.store_transaction_detail(status,transaction_main)
                       tender_bid.epayment_status()
                       return "Payment Successfull", "Success",200
                   return "Tender Bid Doesn't Exist","Error",400
              else:
                   tender_notice=TenderNotice.objects.filter(id=tender_notice_id,user_id=user_id).last()
                   if tender_notice:
                       tender_notice.deposit_paid=True
                       tender_notice.save()  
                       TransactionMain.store_transaction_main(KHALTI,tender_notice_id,tender_notice.user,amount,payment_type,idx,status,fee_for)
                       return "Payment Successfull", "Success",200 
                   return "Tender Bid Doesn't Exist","Error",400
       except Exception as e:
           return str(e),'Error',500
   return str(response.json()["detail"]),'Error',400
    


