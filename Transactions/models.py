from django.db import models
from Tender.models import CreatedUpdatedBase, TenderNotice
from User.models import User
from constants import COMPLETED

# Create your models here.


class TransactionMain(CreatedUpdatedBase):
    description = models.TextField()
    amount = models.FloatField()
    # voucher_no = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100)
    status=models.CharField(max_length=30,default="Pending")
    transaction_idx=models.CharField(max_length=255)
    tender_notice=models.ForeignKey(TenderNotice,null=True, on_delete=models.SET_NULL,related_name="transaction_main")
    fee_for=models.CharField(max_length=100)
    
    @classmethod
    def store_transaction_main(cls,payment_method,tender_notice_id,user,amount,payment_type,tid,status,fee_for):
        description=f'Bid Fee paid by {user.full_name} of {amount}'
        transaction_main= cls.objects.create(transaction_idx=tid,status=status,
        description=description,amount=amount, payment_method=payment_method,user=user, tender_notice_id=tender_notice_id,payment_type=payment_type, fee_for=fee_for
        )
        return transaction_main

    def __str__(self):
            return self.description


class Ledger(models.Model):
    name = models.CharField(max_length=40)
    groupcode = models.IntegerField(default=0)
    has_sub_code = models.BooleanField(default=False)

    def get_ledger( ledger_head):
        ledger = Ledger.objects.filter(name__iexact= ledger_head).last()
        return ledger

    def __str__(self):
        return self.name


class TransactionDetail(CreatedUpdatedBase):
    description = models.TextField()
    debit = models.FloatField()
    credit = models.FloatField()
    transaction_main = models.ForeignKey(
        TransactionMain, on_delete=models.CASCADE)
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE)

    @staticmethod
    def store_transaction_detail(status,transaction_main):
        if status == COMPLETED:
            cash_description= f'Cash has been paid by { transaction_main.user.full_name}'
            fee_description= f'Fee Received From  {transaction_main.user.full_name}'
            fee_head = Ledger.get_ledger('fee')
            cash_head = Ledger.get_ledger('cash')

            TransactionDetail.objects.create(description=fee_description,debit=transaction_main.amount, credit = 0, transaction_main_id=transaction_main.id,ledger_id=fee_head.id)
            TransactionDetail.objects.create(description=cash_description,credit=transaction_main.amount, debit = 0, transaction_main_id=transaction_main.id,ledger_id=cash_head.id)
           


    def __str__(self):
        return self.description

  
class BidFee(models.Model):
    bid_fee=models.FloatField()
    pricing_min=models.FloatField()
    pricing_max=models.FloatField()

    def __str__(self):
        return f'bid_fee {self.bid_fee} pricing_min {self.pricing_min} pricing_max {self.pricing_max}'
    
    
