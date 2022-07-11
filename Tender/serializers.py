
from rest_framework import serializers
from .models import *
from User.models import User
from datetime import datetime
import pytz
utc = pytz.UTC
from django.db.models import Value, BooleanField,TextField
from django.db.models import F
from Tender.services.calculate_tender_boq import calculate_tender_boq


class TenderBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderBid
        exclude = ["rejection_reason"]

    def validate(self, data):
        tender_notice = dict(data).get('tender_notice', None)
        if TenderNotice.objects.get(pk=tender_notice.id).submission_date <= utc.localize(datetime.now()):
            raise serializers.ValidationError(
                {"submission_date": "You can't submit as submission deadline is already over."})
        return super().validate(data)


class TenderNoticePOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderNotice
        exclude = ["bid_bond_security_amount"]

class TenderNoticeSerializer(serializers.ModelSerializer):
    notice_category = serializers.SerializerMethodField('get_notice_category')
    procurement_type = serializers.SerializerMethodField(
        'get_procurement_type')
    project_category = serializers.SerializerMethodField(
        'get_project_category')
    award_result = serializers.SerializerMethodField(source='get_award_result')
    boq = serializers.SerializerMethodField('get_tender_boq')
    public_entity_name = serializers.SerializerMethodField(
        'get_public_entity_name')
    rejection_reason = serializers.SerializerMethodField(
        source='get_rejection_reason')
    extra_info = serializers.SerializerMethodField(
        'get_extra_info')

    class Meta:
        model = TenderNotice
        fields = ['id', 'remaining_days','bid_bond_security_amount','tender_number', 'extra_info', 'notice_category', 'procurement_type', 'project_category', 'title', 'district', 'publishing_date', 'submission_date','boq_sum','amendment',
                   'bid_bond_validity', 'document_needed', 'bank_name', 'branch', 'account_number', 'user', 'remaining_days', 'boq', 'award_result', 'public_entity_name', 'rejection_reason', 'deposit_paid']
    
    def get_notice_category(self, obj):
        return obj.notice_category.annotate(value=F('id'), label=F('name')).values('value', 'label')

    def get_procurement_type(self, obj):
        return obj.procurement_type.annotate(value=F('id'), label=F('name')).values('value', 'label')

    def get_project_category(self, obj):
        return obj.project_category.annotate(value=F('id'), label=F('name')).values('value', 'label')

    def get_award_result(self, obj):
        result = {}
        try:
            qs = TenderWorkAward.objects.filter(tender_notice=obj).last()
            tender_awarded_user = qs.tender_awarded_user
            result["awarded"]=True if self.context.get("user_id") == qs.tender_awarded_user.id else False
            result['price'] = qs.price
            result['company'] = tender_awarded_user.company_name
            return result
        except:
            return result

    def get_tender_boq(self, obj):
        return calculate_tender_boq(obj.id, serialize=True)
        
    def get_public_entity_name(self, obj):
        user = User.objects.filter(id=obj.user_id).last()
        return user.company_name + ", " + user.district + ", " + user.municipality

    def get_extra_info(self, obj):
        extra_info = {}
        joint_venture_name = ""
        e_payment = ""
        tender_bid = TenderBid.objects.filter(
            tender_notice_id=obj.id, user_id=self.context.get("user_id")).last()
        if tender_bid:
            e_payment = tender_bid.document_bid_status['Fee']['e_payment']["status"]
            joint_venture_name = tender_bid.document_bid_status['Joint_Venture']['joint_venture_name']
        extra_info["joint_venture_name"] = joint_venture_name
        extra_info["e_payment"] = e_payment
        return extra_info

    def get_rejection_reason(self, obj):
        tender_bid = TenderBid.objects.filter(
            tender_notice=obj, user_id=self.context.get('user_id')).last()
        return tender_bid.rejection_reason if tender_bid else None

class TenderNoticeEditSerializer(TenderNoticeSerializer):
    bid_boq = serializers.SerializerMethodField('get_bid_boq')

    class Meta(TenderNoticeSerializer.Meta):
        fields = TenderNoticeSerializer.Meta.fields + ['bid_boq',]

    
    def get_bid_boq(self, obj):
        boq_obj = {}
        boq = []
        sum = 0
        tender_boqs = TenderBOQ.objects.filter(tender_notice=obj.id)
        categorys = tender_boqs.values('category').distinct()
        categorys = categorys if TenderBOQDetail.objects.filter(user_id=self.context.get('user'),tender_boq__in=tender_boqs) else []
        boq_obj['boq_catalog_name']=obj.boq_catalog_name
        for category in categorys:
            boq_data = {}
            boq_data["category"] = category['category']
            tender_boqs = TenderBOQ.objects.filter(category=category['category'])
            items = []
            for tender_boq in tender_boqs:
                tender_boq_detail = TenderBOQDetail.objects.filter(tender_boq =tender_boq,user_id=self.context['user'])
                tender_boq_detail_with_extra_data = tender_boq_detail.annotate(fixed=Value(tender_boq.fixed, output_field=BooleanField())).annotate(item_description=Value(tender_boq.item_description, output_field=TextField())).annotate(unit=Value(tender_boq.unit, output_field=TextField())).values()
                if tender_boq_detail:
                    items.extend(tender_boq_detail_with_extra_data)
            boq_data['item'] = items
            for tender_boq in tender_boq_detail:
                sum += tender_boq.amount
            boq.append(boq_data)
        boq_obj["boq_details"] = boq
        boq_obj["boq_sum"] = sum
        boq_obj["vat_amount"] = (sum * 13) / 100
        return boq_obj



class TenderBOQPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenderBOQ
        fields = ['tender_notice', 'category',
                  'item_description', 'unit', 'quantity', 'rate', 'amount', 'fixed']


class TenderBOQDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderBOQDetail
        exclude = ('created', 'updated')


class TenderWorkAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderWorkAward
        fields = '__all__'

    def validate(self, data):
        tender_notice = dict(data).get('tender_notice', None)
        if TenderWorkAward.objects.filter(tender_notice=tender_notice):
            raise serializers.ValidationError(
                "This Tender Notice Has Already Awarded")
        return super().validate(data)


class BidderBidDetailSerailizer(serializers.Serializer):
    bidder_id = serializers.IntegerField(required=False)
    tender_notice_id = serializers.IntegerField(required=True)


class DocumentFileSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model=DocumentSampleFile
        fields='__all__'
