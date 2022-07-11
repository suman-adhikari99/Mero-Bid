from .models import TenderNotice, TenderBOQ, TenderBOQDetail

def document_needed(data):
    document_needed = data.get("document_needed", None)
    if document_needed.get("bid_letter", False) and document_needed.get("declaration_letter", False):
        document_needed = "Both"
    elif document_needed.get("bid_letter", False):
        document_needed = "bid_letter"
    elif document_needed.get("declaration_letter", False):
        document_needed = "declaration_letter"
    return document_needed


def previous_bank_detail(user_id, data):
    previous_bank_detail = TenderNotice.objects.filter(
        user=user_id).latest('created')
    data["bank_name"] = previous_bank_detail.bank_name
    data["branch"] = previous_bank_detail.branch
    data["account_number"] = previous_bank_detail.account_number
    return data

def tender_award_price(tender_notice_id,awarded_user_id):
    try:
        price = 0
        tender_boq = TenderBOQ.objects.filter(tender_notice_id=tender_notice_id)
        for boq in tender_boq:
            tender_boq_detail = TenderBOQDetail.objects.filter(user_id=awarded_user_id, tender_boq=boq)
            for tender_boq_detail in tender_boq_detail:
                   price += tender_boq_detail.amount
        return price
    except Exception as e:
        return 0
