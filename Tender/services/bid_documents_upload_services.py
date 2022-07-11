from constants import SUBMITTED
from utils.file_register import register_file


def joint_venture_upload(request, tender_bid):
    keys = ['power_of_attorney', 'venture_agreement']
    joint_venture = tender_bid.document_bid_status["Joint_Venture"]
    joint_venture["joint_venture_name"] = request.data.get(
        'joint_venture_name', None)
    
    for key in keys:
        file_needed = True
        if all(v==SUBMITTED for v in (joint_venture['venture_agreement']['status'],joint_venture['power_of_attorney']['status'])):
            file_needed = True if key in request.FILES else False
        if file_needed:      
            joint_venture[key]["file_url"] = register_file(request.FILES[key])
            joint_venture[key]["status"] = SUBMITTED


def fee_upload(request, tender_bid):
    bid_bond_security=tender_bid.tender_notice.bid_bond_security_amount
    if bid_bond_security:
        file_needed = True
        tender_bid_fee = tender_bid.document_bid_status["Fee"]
        if tender_bid_fee["voucher"]["status"] == SUBMITTED:
            file_needed = True if 'voucher' in request.FILES else False
        if file_needed:  
            tender_bid_fee["voucher"]["file_url"] = register_file(
                        request.FILES['voucher'])
            tender_bid_fee["voucher"]["status"] = SUBMITTED       


def document_upload(request, tender_bid):
    document_needed = tender_bid.tender_notice.document_needed
    tender_bid_document = tender_bid.document_bid_status["Document"]
    if document_needed == 'Both':
        keys = ['bid_letter', 'declaration_letter', 'tax_clearence']
    else:
        keys = [document_needed, 'tax_clearence']

    for key in keys:
        file_needed = True
        if tender_bid_document['tax_clearence']['status']==SUBMITTED:
            file_needed = True if key in request.FILES else False
        if file_needed:    
            tender_bid_document[key]["file_url"] = register_file(
                    request.FILES[key])
            tender_bid_document[key]["status"] = SUBMITTED

def boq_file_upload(request,tender_bid):
    file_needed = True
    doc = tender_bid.tender_notice.boq_catalog_name
    if doc:
        if tender_bid.document_bid_status['BOQ']['status'] == SUBMITTED:
            file_needed = True if 'catalogue_file'  in request.FILES else False
        if file_needed:
            tender_bid.document_bid_status["BOQ"]["file_url"] = register_file(
                    request.FILES['catalogue_file'])
    


def document_bid_status(tender_bid):
    if tender_bid.status != SUBMITTED:
        document_needed = tender_bid.tender_notice.document_needed
        tender_bid_document = tender_bid.document_bid_status["Document"]
        tender_bid_fee = tender_bid.document_bid_status["Fee"]
        tender_boq = tender_bid.document_bid_status['BOQ']
        bid_bond_security=tender_bid.tender_notice.bid_bond_security_amount
        if document_needed == 'Both':
            document = True if all(v == SUBMITTED for v in (
                tender_bid_document['bid_letter']["status"], tender_bid_document['declaration_letter']["status"], tender_bid_document["tax_clearence"]["status"])) else False
        else:
            document = True if all(v == SUBMITTED for v in (
                tender_bid_document[document_needed]["status"], tender_bid_document["tax_clearence"]["status"])) else False
        if bid_bond_security:
            other = True if all(v == SUBMITTED for v in (
            tender_bid_fee['e_payment']["status"], tender_bid_fee["voucher"]["status"], tender_boq['status'])) else False
        else:
            other = True if all(v == SUBMITTED for v in (
            tender_bid_fee['e_payment']["status"], tender_boq['status'])) else False
        if document and other:
            tender_bid.status = SUBMITTED
           

def get_bid_documents(tender_bid):
    bid_document_data = {'Fee': {}, 'Document': {}, 'Joint_Venture': {}}
    tender_bid_document = tender_bid.document_bid_status
    for key in tender_bid_document.keys():
        if key != 'BOQ':
            for item in tender_bid_document[key].keys():
                if key == 'Joint_Venture' and tender_bid_document[key]['joint_venture_name']:
                    bid_document_data[key]['joint_venture_name'] = tender_bid_document[key]['joint_venture_name']
                if item != 'joint_venture_name':
                    if tender_bid_document[key][item]['status'] == SUBMITTED:
                        bid_document_data[key][item] = tender_bid_document[key][item]['file_url']
    return bid_document_data
