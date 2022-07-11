from constants import *
from e_bidding.api_render import api_response_render
from Tender.serializers import *
from Tender.services.bid_documents_upload_services import *
from decorator.auth_decorator import auth_required
from decorator.is_bidder import is_bidder
from Tender.helper import *
from rest_framework.generics import GenericAPIView
import json
from Tender.services.calculate_tender_boq import calculate_tender_boq


class TenderBOQView(GenericAPIView):
    http_method_names = ['get']

    def post(self, request, tender_notice_id, update=False):
        data = {}
        try:
            if update:
                boq_ids= list(filter(lambda id: id,[boq['item'][i].get('id')  for boq in request.data['BOQ'] for i, id in enumerate( boq['item'])]))
                TenderBOQ.objects.filter(tender_notice_id = tender_notice_id).exclude(id__in=boq_ids).delete()
            data["tender_notice"] = tender_notice_id
            for BOQ in request.data['BOQ']:
                data["category"] = BOQ['category']
                for item in BOQ['item']:
                    data["item_description"] = item['item_description']
                    data["unit"] = str(item['unit'])
                    data["quantity"] = item['quantity']
                    data["rate"] = float(item['rate'])
                    data["amount"] = float(
                        item['rate']) * float(item['quantity'])
                    data["fixed"] = item["fixed"]
                    if update and item.get('id', None):
                        tender_boq_obj = TenderBOQ.objects.get(id=item['id'])
                        tender_boq = TenderBOQPostSerializer(tender_boq_obj,data=data)
                    else:   
                        tender_boq = TenderBOQPostSerializer(data=data)
                    if tender_boq.is_valid(raise_exception=True):
                            tender_boq.save()
            calc_bond_security=request.data.get('bid_bond_security',None)
            calculate_tender_boq(tender_notice_id, calc_bond_security)
            return api_response_render(data={'tender_notice_id':tender_notice_id},status_msg="Tender publish successfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)


class TenderBOQDetailView(GenericAPIView):
    @auth_required()
    @is_bidder()
    def post(self, request, user_id):
        try:
            grand_total=request.data.get('grand_total')
            tender_notice_id=request.data.get('tender_notice_id',None)
            tender_notice=TenderNotice.objects.filter(id=tender_notice_id).last()
            tender_notice_category=tender_notice.notice_category.all().first().name
            if "auction" in tender_notice_category.lower():
                if grand_total<tender_notice.boq_sum:
                    return api_response_render(status_msg=f"Amount can't be less than boq amount ({tender_notice.boq_sum})", status_type='Error', status_code=400)
            else:
                if grand_total>tender_notice.boq_sum:
                    return api_response_render(status_msg=f"Amount can't be greater than boq amount ({tender_notice.boq_sum})", status_type='Error', status_code=400)
            tender_bid = TenderBid.objects.filter(
                tender_notice_id=tender_notice_id, user_id=user_id).last()
            boq_file_upload(request, tender_bid)
            tender_boq=TenderBOQ.objects.filter(tender_notice_id=tender_notice_id).values_list('id')
            TenderBOQDetail.objects.filter(user_id=user_id,tender_boq__in=tender_boq).delete()
            for boq in json.loads(request.data['boq']):   
                for item in boq['item']: 
                    TenderBOQDetail.objects.create(tender_boq_id=item['id'], user_id=user_id,amount= item['amount'], rate= item['rate'], quantity= item['quantity'] )
            tender_bid.document_bid_status['BOQ']['status'] = SUBMITTED 
            document_bid_status(tender_bid)
            tender_bid.save()
            return api_response_render(status_msg="BOQ Submitted Sucessfully", status_type='Success', status_code=200)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

