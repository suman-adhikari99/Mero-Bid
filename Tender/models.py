from django.db import models
from constants import *
from django.contrib.postgres.fields import JSONField
from User.models import *
from constants import IN_PROGRESS, SUBMITTED
from Tender.services.bid_documents_upload_services import document_bid_status
from datetime import timedelta, datetime, date
import pytz
utc = pytz.UTC
from rest_framework.exceptions import NotFound

# Create your models here.


class CreatedUpdatedBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NoticeCategory(CreatedUpdatedBase):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class ProcurementType(CreatedUpdatedBase):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class ProjectCategory(CreatedUpdatedBase):
    name = models.CharField(max_length=100)
    procurement_type = models.ForeignKey(
        ProcurementType, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class TenderPrice(CreatedUpdatedBase):
    tender_price = models.CharField(max_length=100)

    def __str__(self):
        return str(self.tender_price)


CATEGORY_CHOICES = (("Result", "Result"), ("Bids", "Bids"))


class TenderNotice(CreatedUpdatedBase):
    tender_number= models.CharField(max_length=254)
    title = models.CharField(max_length=254)
    district = models.CharField(max_length=100)
    notice_category = models.ManyToManyField(
        NoticeCategory, related_name="notice_category"
    )
    procurement_type = models.ManyToManyField(
        ProcurementType, related_name="procurement_type"
    )
    project_category = models.ManyToManyField(
        ProjectCategory, related_name="project_category"
    )
    publishing_date = models.DateField()
    submission_date = models.DateTimeField()
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="Bids"
    )
    user = models.ForeignKey("User.User", on_delete=models.CASCADE)
    bid_bond_security_amount = models.DecimalField(
        max_digits=120, decimal_places=2, null=True,blank=True)
    bid_bond_validity = models.IntegerField()
    document_needed = models.CharField(max_length=120)
    bank_name = models.CharField(max_length=120)
    branch = models.CharField(max_length=30)
    account_number = models.CharField(max_length=120)
    boq_catalog_name=models.CharField(max_length=120,null=True,blank=True)
    deposit_paid=models.BooleanField(default=False)
    deposit_refunded=models.BooleanField(default=False)
    amendment=models.BooleanField(default=False)
    boq_sum=models.FloatField( null=True,blank=True)

    @property
    def current_date(self):
        return date.today()
    @property
    def remaining_days(self):
        if self.submission_date.date()>self.current_date:
            return (self.submission_date.date() -self.current_date).days
        return 0

    def tender_notice_dict(self):
        return {"id": self.id}

    @staticmethod
    def set_values(data):
        procurement = ProcurementType.objects.get(
            id=data["procurement_type"]).name
        project = ProjectCategory.objects.get(
            id=data["project_category"]).name
        data["title"] =f" {procurement} Notice for {project}"
        data["notice_category"]=[data['notice_category']]
        data['procurement_type']=[data['procurement_type']]
        data['project_category']=[data['project_category']]
        data["submission_date"] = datetime.strptime(
            data.get("submission_date"), '%Y-%m-%d')+timedelta(hours=12)
        return data

    @classmethod
    def get_tender_notice(cls,pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            raise NotFound(TENDER_NOTICE_DOESNOT_EXIST)

    def __str__(self):
        return str(self.id)


class TenderBOQ(CreatedUpdatedBase):
    tender_notice = models.ForeignKey(
        TenderNotice, on_delete=models.CASCADE, related_name="tender_notice")
    category = models.CharField(max_length=300)
    item_description = models.TextField(max_length=None)
    unit = models.CharField(max_length=100)
    quantity = models.IntegerField()
    rate = models.FloatField()
    amount = models.FloatField()
    fixed = models.BooleanField(default=False)

    def __str__(self):
        return ("pk = " + str(self.id) + " Tender notice id = " + str(self.tender_notice) + " and category = " + str(self.category) + " user = " + str(self.tender_notice.user.id))


class TenderBOQDetail(CreatedUpdatedBase):
    tender_boq = models.ForeignKey(TenderBOQ, on_delete=models.CASCADE)
    user = models.ForeignKey("User.User", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    rate = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return str("pk = " + str(self.id) + " tender_boq_id = " + str(self.tender_boq) + " user = " + str(self.user))


class TenderBid(CreatedUpdatedBase):
    tender_notice = models.ForeignKey(
        TenderNotice, on_delete=models.CASCADE, related_name="tender_bids"
    )
    user = models.ForeignKey("User.User", on_delete=models.CASCADE)
    rejection_reason= models.CharField(max_length=255,blank=True,null=True)
    status = models.CharField(max_length=100, default=IN_PROGRESS)
    document_bid_status = JSONField(default=TENDER_BID_DEFAULT_STATUS)

    def epayment_status(self):
        self.document_bid_status["Fee"]["e_payment"]["status"] = SUBMITTED
        document_bid_status(self)
        self.save()

    def documents_link(self):
        document_link = self.document_bid_status
        data = {
            "joint_venture_name": document_link['Joint_Venture']['joint_venture_name'],
           "venture_agreement":document_link['Joint_Venture']['venture_agreement']['file_url'],
            "power_of_attorney":document_link['Joint_Venture']['power_of_attorney']['file_url'],
            "e_payment":document_link['Fee']['e_payment']['status'],
            "voucher":document_link['Fee']['voucher']['file_url'],
            "bid_letter":document_link["Document"]["bid_letter"]["file_url"],
            "declaration_letter":document_link['Document']['declaration_letter']['file_url'],
            "tax_clearence":document_link['Document']['tax_clearence']['file_url'],
            "boq_catalog_file":document_link['BOQ']['file_url']
        }   
        return data 


class TenderWorkAward(CreatedUpdatedBase):
    tender_awarded_user = models.ForeignKey(
        "User.User", on_delete=models.CASCADE)
    tender_notice = models.ForeignKey(TenderNotice, on_delete=models.CASCADE,related_name='tenderworkaward')
    work_awarded = models.CharField(
        max_length=200, null=True, blank=True)
    tender_number = models.CharField(
        max_length=100,  null=True, blank=True)
    price = models.FloatField()

    def __str__(self):
        return (
            "Tender notice id = "
            + str(self.tender_notice)
            + " and id = "
            + str(self.id)
        )



class DocumentSampleFile(models.Model):
    joint_venture=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    power_of_attorney= models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    bank_guarenty=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    registration_certificate_back = models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    registration_certificate_front=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    bid_letter=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    declaration_letter=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    company_tax_clearence=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    pan_vat_certificate =models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    liscense_back =models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    liscense_front=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    boq_catalog_file=models.FileField(
        upload_to='document_sample/',null=True, blank=True)
    
