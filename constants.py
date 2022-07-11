# constant values
TENDER_NOTICE_DOESNOT_EXIST="Tender Notice Doesn't Exist"
TENDER_BID_DOESNOT_EXIST="Tender Bid Doesn't Exist"
#status
SUBMITTED="Submitted"
WITH_DRAWN="Withdrawn"
IN_PROGRESS = 'In-progress'
PENDING="Pending"
COMPLETED = "Completed"
KHALTI = "Khalti"
ESEWA= "Esewa"
WALLET = "Wallet"

#tender bid document status
TENDER_BID_DEFAULT_STATUS = {'Joint_Venture':{
	'joint_venture_name': '',
	'venture_agreement': {
		'file_url': '',
		'status': 'pending'
	},
	'power_of_attorney': {
		'file_url': '',
		'status': 'pending'
	}
},
  'Fee':{
	'e_payment': {
		'file_url': '',
		'status': 'pending'
	},
	'voucher': {
		'file_url': '',
		'status': 'pending'
	}
},
  'BOQ':{
		'file_url':'',
		'status': 'pending'
},
  'Document':{
	'bid_letter': {
		'file_url': '',
		'status': 'pending'
	},
	'declaration_letter': {
		'file_url': '',
		'status': 'pending'
	},
	'tax_clearence': {
		'file_url': '',
		'status': 'pending'
	}
}
}
# we pass the dictionary format data to the model.
# then, we access it in the views.
