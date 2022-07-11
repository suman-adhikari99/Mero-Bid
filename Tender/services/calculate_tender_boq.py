from Tender.models import TenderNotice, TenderBOQ
from Transactions.models import BidFee

def calculate_tender_boq(id, calc_bond_security=False,serialize=False):
    tender_boq = TenderBOQ.objects.filter(tender_notice=id)
    category = tender_boq.values('category').distinct()
    boq_obj = {}
    boq = []
    sum = 0
    boq_obj['boq_catalog_name']=TenderNotice.objects.get(id=id).boq_catalog_name
    for category in category:
        boq_data = {}
        boq_data["category"] = category['category']
        tender_boqs = TenderBOQ.objects.filter(
            category=category['category'], tender_notice=id)
        boq_data['item'] = tender_boqs.values()
        for tender_boq in tender_boqs:
            sum += tender_boq.amount
        boq.append(boq_data)
    boq_obj["boq_details"] = boq
    boq_obj["boq_sum"] = sum
    vat_amount = (sum * 13) / 100
    boq_obj["bid_fee"]= BidFee.objects.filter(pricing_min__lte=sum,pricing_max__gte=sum).first().bid_fee
    if not serialize:
        if calc_bond_security:
            TenderNotice.objects.filter(id=id).update(bid_bond_security_amount =(sum*2.5)/100,boq_sum=sum+ vat_amount)
        else :
            TenderNotice.objects.filter(id=id).update(bid_bond_security_amount =0,boq_sum=sum+ vat_amount)
    boq_obj["vat_amount"] = vat_amount
    return boq_obj

