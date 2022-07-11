from datetime import timedelta, datetime
from constants import *
from e_bidding.api_render import api_response_render
from Tender.serializers import *
from Tender.services.bid_documents_upload_services import *
from decorator.auth_decorator import auth_required
from decorator.is_publisher import is_publisher
from Tender.helper import *
from Tender.services.filter_service import filter_tenders
from Tender.paginations import CustomPagination
from rest_framework.generics import GenericAPIView
import pytz
utc = pytz.UTC
from ..tasks import tender_change_mail
from .tender_boq_views import TenderBOQView


class TenderNoticeView(GenericAPIView):
    pagination_class = CustomPagination

    def get(self, request, pk=None):
        try:
            if pk == None:
                serialize_data = filter_tenders(self, request, 'Bids')
            else:
                if 'access_token' not in request.COOKIES:
                    return api_response_render(status_msg="Authentication failed for user, please login",
                                               status_type="ERROR", status_code=401)
                user = User.user_from_token(request.COOKIES['access_token'])
                serialize_data = TenderNoticeSerializer(
                    TenderNotice.get_tender_notice(pk),context={"user_id":user['user_id']}).data
                tender_bid = TenderBid.objects.filter(
                    tender_notice_id=pk, user_id=user['user_id']).first()
                if tender_bid:
                    bid_document_data = get_bid_documents(tender_bid)
                    serialize_data['bid_document_data'] = bid_document_data
            return api_response_render(data=serialize_data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

    # def document_and_bank_details(self, data, user_id):
    #     data["document_needed"] = document_needed(data)
    #     if data['same_as_previous']:
    #         try:
    #             data = previous_bank_detail(user_id, data)
    #         except TenderNotice.DoesNotExist:
    #             return api_response_render(status_msg="Tender notice unavailable to fetch previous bank details", status_type='Error', status_code=400)

    @auth_required()
    @is_publisher()
    def post(self, request, user_id):
        data = request.data
        data["user"] = user_id
        TenderNotice.set_values(data)
        data["document_needed"] = document_needed(data)
        tender_notice = TenderNoticePOSTSerializer(data=data)
        if tender_notice.is_valid():
            tender_notice_id = tender_notice.save()
            response = TenderBOQView.post(
                self, request, tender_notice_id.id, update=False)
            return response
        return api_response_render(status_msg=tender_notice.errors, status_type='Error', status_code=400)

    @auth_required()
    @is_publisher()
    def put(self, request, user_id, pk):
        data = request.data
        tender_notice = TenderNotice.get_tender_notice(pk)
        if tender_notice.user_id != user_id:
            return api_response_render(status_msg="You are not a original publisher", status_type='error', status_code=400)
            
        if tender_notice.amendment:
            return api_response_render(status_msg="Amendment Notice can't be modify", status_type='error', status_code=400)
        if utc.localize(datetime.now()+timedelta(days=7))>tender_notice.submission_date:
            return api_response_render(status_msg="Restricted to modify tender", status_type='error', status_code=400) 
        data["amendment"]=True
        TenderNotice.set_values(data)
        data["document_needed"] = document_needed(data)
        serialize_tender_notice = TenderNoticePOSTSerializer(
            tender_notice, data=data, partial=True)
        if serialize_tender_notice.is_valid():
            serialize_tender_notice.save()
            email_of_bidder=[obj.user.email for  obj in TenderBid.objects.filter(tender_notice__id=pk)]
            tender_change_mail(email_of_bidder,tender_notice.title)
            response = TenderBOQView.post(
                self, request, pk, update=True)
            return response
        return api_response_render(status_msg=serialize_tender_notice.errors, status_type='Error', status_code=400)

    @auth_required()
    @is_publisher()
    def delete(self, request, user_id, pk):
        tender_notice = TenderNotice.get_tender_notice(pk)
        if tender_notice.user_id == user_id:
            tender_notice.delete()
            return api_response_render(status_msg="Delete Successfully", status_type='Success', status_code=200)
        return api_response_render(status_msg="You can't delete this notice because you are not the original publisher of this notice.", status_type='Error', status_code=400)


class TenderResult(GenericAPIView):
    pagination_class = CustomPagination
    def get(self, request, pk=None):
        if pk == None:
            data = filter_tenders(self, request, 'Result')
            return api_response_render(data=data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)


class TenderWorkAwardView(GenericAPIView):
    @auth_required()
    @is_publisher()
    def post(self, request, user_id):
        data = request.data
        data['tender_notice'] = data.get('tender_notice_id', None)
        data['tender_awarded_user'] = data.get('bidder_id', None)
        tender_bid = TenderBid.objects.filter(
            tender_notice_id=data['tender_notice'], user_id=data['tender_awarded_user']).last()
        if tender_bid and tender_bid.status == SUBMITTED:
            data['price'] = tender_award_price(
                data['tender_notice'], data['tender_awarded_user'])
            tender_award = TenderWorkAwardSerializer(data=data)
            if tender_award.is_valid():
                tender_award.save()
                tender_notice = TenderNotice.objects.filter(
                    id=data['tender_notice_id']).last()
                tender_notice.category = 'Result'
                tender_notice.save()
                if tender_bid.rejection_reason:
                    tender_bid.rejection_reason= None
                    tender_bid.save()
                return api_response_render(data=data, status_msg="Tender awared successfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=tender_award.errors, status_type='Error', status_code=400)
        return api_response_render(status_msg="Bidder hasn't submitted all documents", status_type='Error', status_code=400)


class TenderAttribute(GenericAPIView):
    def get(self, request):
        data = {}
        procurement_type_name = ProcurementType.objects.extra(
            select={'value': 'id', 'label': 'name'}).values('label', 'value')
        notice_category_name = NoticeCategory.objects.extra(
            select={'value': 'id', 'label': 'name'}).values('label', 'value')
        project_name = ProjectCategory.objects.extra(
            select={'value': 'id', 'label': 'name'}).values('label', 'value')
        data['notice_category'] = notice_category_name
        data['procurement_type'] = procurement_type_name
        data['project_category'] = project_name
        return api_response_render(data=data,status_msg="Data Fetch Successfully", status_type='Successs', status_code=200)


class PublisherBankDetail(GenericAPIView):
    @auth_required()
    @is_publisher()
    def get(self, request, user_id):
        try:
            tender_notice = TenderNotice.objects.filter(user_id=user_id).last()
            data = {
                'bank_name': tender_notice.bank_name,
                'branch': tender_notice.branch,
                'account_number': tender_notice.account_number
            }
            return api_response_render(data=data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400)


class DocumentSampleFileView(GenericAPIView):
    def get(self,request, pk=None):
        try:
            if pk:
               sample= DocumentSampleFile.objects.get(id=pk)
               sample_data=DocumentFileSampleSerializer(sample).data
            else:
                sample=DocumentSampleFile.objects.all()
                sample_data=DocumentFileSampleSerializer(sample,many=True).data
            return api_response_render(data=sample_data,status_msg="Data Fetch successfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

