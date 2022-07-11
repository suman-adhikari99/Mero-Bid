from datetime import timedelta, datetime
from constants import *
from ..helper import *
from e_bidding.api_render import api_response_render
from Tender.serializers import *
from Tender.services.bid_documents_upload_services import *
from decorator.auth_decorator import auth_required
from decorator.is_publisher import is_publisher
from decorator.is_bidder import is_bidder
from rest_framework.generics import GenericAPIView
import pytz
utc = pytz.UTC


class TenderBidView(GenericAPIView):
    def get_tender_bid(self, tender_notice_id, user_id):
        return TenderBid.objects.filter(tender_notice_id=tender_notice_id, user_id=user_id).exists()

    @auth_required()
    @is_bidder()
    def post(self, request, user_id):
        try:
            data = request.data
            data["user"] = user_id
            data["tender_notice"] = data.get('tender_notice_id', None)
            if self.get_tender_bid(data["tender_notice"], user_id):
                return api_response_render(status_msg="Data already exist. Please check in my bid section", status_type='Success', status_code=202)
            tender_bid = TenderBidSerializer(data=data)
            if tender_bid.is_valid():
                tender_bid.save()
                return api_response_render(data=tender_bid.data, status_msg="Your Bid is in progress", status_type='Success', status_code=200)
            return api_response_render(status_msg=tender_bid.errors, status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

    @auth_required()
    def get(self, request, user_id, tender_notice_id=None):
        try:
            data = {}
            tender_notice = TenderNotice.objects.get(id=tender_notice_id)
            submission_date = tender_notice.submission_date+timedelta(hours=2)
            data = dict(TenderNoticeSerializer(tender_notice, many=False).data)
            # if utc.localize(datetime.now()) > submission_date:
            if True:
                all_bidder = []
                tender_bids = TenderBid.objects.filter(
                    tender_notice=int(tender_notice_id), status=SUBMITTED)
                for tender_bid in tender_bids:
                    bidder_data = {}
                    bidder_user = tender_bid.user
                    bidder_data["bid_id"] = tender_bid.id
                    bidder_data["bidder_id"] = bidder_user.id
                    bidder_data["bidder_name"] = bidder_user.full_name
                    bidder_data["organization_name"] = bidder_user.company_name
                    bidder_data["organization_category"] = bidder_user.organization_category
                    bidder_data["location"] = bidder_user.location
                    bidder_data["grand_total"] = tender_award_price(tender_notice_id, bidder_user.id)
                    bidder_data["status"] = tender_bid.status
                    if TenderWorkAward.objects.filter(tender_awarded_user=tender_bid.user, tender_notice=tender_notice_id).last():
                        bidder_data["status"] = "Awarded"
                    elif TenderBid.objects.filter(tender_notice_id=tender_notice_id, user=tender_bid.user,rejection_reason__isnull=False).last():
                        bidder_data["status"] = "Disqualified"
                    all_bidder.append(bidder_data)      
            data["bider_lists"] = all_bidder
            return api_response_render(data=data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)


class UploadView(GenericAPIView):
    def get_tender_bid(self, tender_notice_id, user_id):
        try:
            return TenderBid.objects.filter(tender_notice_id=tender_notice_id, user_id=user_id).latest('-created')
        except TenderBid.DoesNotExist:
            raise NotFound(TENDER_BID_DOESNOT_EXIST)

    @auth_required()
    @is_bidder()
    def post(self, request, user_id):
        type = request.data.get("type", None)
        tender_notice_id = int(request.data.get('tender_notice_id', None))
        try:
            tender_notice = TenderNotice.get_tender_notice( tender_notice_id)
            tender_bid = self.get_tender_bid(tender_notice_id, user_id)
            # if tender_notice.submission_date >= utc.localize(datetime.now()):
            if True:
                if type == 'Joint_Venture':
                    joint_venture_upload(request, tender_bid)
                elif type == 'Fee':
                    fee_upload(request, tender_bid)
                elif type == 'Document':
                    document_upload(request, tender_bid)
                document_bid_status(tender_bid)
                tender_bid.save()
                return api_response_render(status_msg=f"{type} is uploaded successfully ", status_type='Success', status_code=200)
            return api_response_render(status_msg=f"Submission Date is already over", status_type='Error', status_code=400)
        except NotFound as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=f"{str(e)} file is needed", status_type='Error', status_code=500)


class MyBid(GenericAPIView):
    @auth_required()
    def get(self, request, user_id):
        is_publisher = User.is_publisher(user_id)
        if is_publisher:
            all_bids = TenderNotice.objects.filter(user_id=user_id)
            submitted_items = all_bids.filter(deposit_paid=True)
            inprogresss_items = all_bids.filter(deposit_paid=False)
            withdrawn_or_awarded_items = TenderNotice.objects.filter(user_id=user_id,tenderworkaward__tender_notice__in=all_bids)
        else:
            all_bids = TenderNotice.objects.filter(tender_bids__user_id=user_id)
            submitted_items =  TenderNotice.objects.filter(tender_bids__user_id=user_id, tender_bids__status=SUBMITTED)
            inprogresss_items = TenderNotice.objects.filter(tender_bids__user_id=user_id, tender_bids__status=IN_PROGRESS)
            withdrawn_or_awarded_items = TenderNotice.objects.filter(tender_bids__user_id=user_id, tender_bids__status=WITH_DRAWN)

        serialized_submitted_items = TenderNoticeSerializer(
            submitted_items, many=True, context={'user_id': user_id})
        serialized_inprogresss_items = TenderNoticeSerializer(
            inprogresss_items, many=True, context={'user_id': user_id})
        serialized_withdrawn_or_awarded_items = TenderNoticeSerializer(
            withdrawn_or_awarded_items, many=True, context={'user_id': user_id})

        data = {
            "In_progress": serialized_inprogresss_items.data,
            "Submitted": serialized_submitted_items.data,
            "Withdrawn_or_awarded": serialized_withdrawn_or_awarded_items.data,
        }

        # if is_publisher:
        #     data.pop('Withdrawn', None)
        # else:
        #     data.pop('all_bids', None)

        return api_response_render(data=data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)

    @auth_required()
    @is_bidder()
    def put(self, request, user_id,tender_notice_id):
        try:
            request_type = request.data.get('request_type', None)
            tender_bid = TenderBid.objects.filter(tender_notice_id=tender_notice_id, user_id=user_id).last()
            tender_bid.status = WITH_DRAWN if request_type in [0,'0'] else SUBMITTED 
            tender_bid.save()
            return api_response_render(status_msg=f"Bid {tender_bid.status} Successfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=200)



class BidderBidDetail(GenericAPIView):
    @auth_required()
    def get(self, request, user_id):
        try:
            bidder_id=user_id
            if User.is_publisher(user_id):
                 bidder_id = request.GET.get('bidder_id', None)
            tender_notice_id = request.GET.get('tender_notice_id', None)
           
            serializer = BidderBidDetailSerailizer(data=request.GET)
            if serializer.is_valid():
                tender_bid = UploadView.get_tender_bid(
                    self, int(tender_notice_id), int(bidder_id))
                tender_notice = TenderNotice.objects.get(id=int(tender_notice_id))
                organization_detail = User.objects.values('company_name', 'organization_category', 'office_email',
                                                          'website_url', 'company_contact_no', 'province', 'district', 'municipality').get(id=bidder_id)
                data = {
                    'organization_detail': organization_detail,
                    'documents': tender_bid.documents_link(),
                    'tender_notice': TenderNoticeEditSerializer(tender_notice,context={'user': bidder_id}).data
                }
                return api_response_render(data=data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=serializer.errors, status_type='Error', status_code=400)
        except NotFound as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)


class TenderBidRejection(GenericAPIView):
    @auth_required()
    @is_publisher()
    def put(self, request, user_id):
        try:
            rejection_reason = request.data.get("rejection_reason", None)
            tender_notice_id = request.data.get("tender_notice_id", None)
            bidder_id = request.data.get("bidder_id", None)
            if rejection_reason:
                tender_work_award = TenderWorkAward.objects.filter(tender_notice=tender_notice_id, tender_awarded_user_id=bidder_id)
                if tender_work_award:
                      tender_work_award.first().delete()
                tender_bid = TenderBid.objects.filter(tender_notice_id=tender_notice_id, user_id=bidder_id).last()
                tender_bid.rejection_reason = rejection_reason
                tender_bid.save()
                return api_response_render(status_msg="Bid is rejected successfully", status_type='Success', status_code=200)
            return api_response_render(status_msg="Rejection Reason is needed", status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

