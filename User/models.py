
from django.contrib.auth.models import AbstractUser
from django.db import models
from Tender.models import CreatedUpdatedBase
from Tender.models import NoticeCategory, ProcurementType, TenderNotice, ProjectCategory, TenderPrice

from simple_history.models import HistoricalRecords
from Tender.models import *
import jwt
from e_bidding.settings import SIMPLE_JWT
import uuid
from rest_framework.exceptions import NotFound



# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=100,blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    organization_category = models.CharField(
        max_length=100, blank=True, null=True)
    office_email = models.EmailField(max_length=100,blank=True, null=True)
    website_url = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    company_contact_no = models.CharField(max_length=100,blank=True, null=True)
    registration_certificate_front = models.FileField(
        upload_to='user_documents/')
    registration_certificate_back = models.FileField(
        upload_to='user_documents/',null=True, blank=True)
    pan_vat_certificate = models.FileField(upload_to='user_documents/')
    liscense_front = models.FileField(
        upload_to='user_documents/', null=True, blank=True)
    liscense_back = models.FileField(
        upload_to='user_documents/', null=True, blank=True)

    email_verification_token = models.UUIDField(default=uuid.uuid4, null=True)
    password_reset_token = models.UUIDField(null=True, blank=True)
    email_verification = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.email+str(self.id))

    @property
    def full_name(self):
        return ' '.join(filter(None, (self.first_name, self.middle_name, self.last_name)))

    @property
    def location(self):
        return ' ,'.join(filter(None, (self.municipality, self.district, self.province)))

    @classmethod
    def user_from_token(self, token):
        user = jwt.decode(token, SIMPLE_JWT['SIGNING_KEY'], algorithms=[
                          SIMPLE_JWT['ALGORITHM']],)
        return user

    @classmethod
    def is_publisher(self, user_id):
        user_role = UserRole.objects.filter(user_id=user_id).last()
        if str(user_role.role) == "Publisher":
            return True
        return False

    @classmethod
    def check_user_email_token(self, token):
        try:
            return User.objects.get(email_verification_token=token)
        except Exception as e:     
            raise NotFound("User Token Doesn't Exist") 

    @classmethod
    def check_user_password_reset_token(self, token):
        try:
            return User.objects.get(password_reset_token=token)
        except Exception as e:     
            raise NotFound("User Token Doesn't Exist")     

class UserInterest(CreatedUpdatedBase):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    procument_id = models.ForeignKey(ProcurementType, on_delete=models.CASCADE)
    notice_id = models.ForeignKey(TenderNotice, on_delete=models.CASCADE)
    project_id = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE)
    tender_price_id = models.ForeignKey(TenderPrice, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_id)


class Role(CreatedUpdatedBase):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class UserRole(CreatedUpdatedBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


