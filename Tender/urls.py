from django.urls import path, re_path
from .view.tender_bid_views import *
from .view.tender_views import *
from .view.tender_boq_views import *

app_name = "Tender"
urlpatterns = [
    path("v1/tender_notice", TenderNoticeView.as_view()),
    path("v1/tender_notice/<int:pk>", TenderNoticeView.as_view()),
    path("v1/tender_boq", TenderBOQView.as_view()),
    path("v1/tender_bid", TenderBidView.as_view()),
    re_path(r"^v1/tender_bid/(?P<tender_notice_id>\d+)$",TenderBidView.as_view()),
    path("v1/tender/document/upload", UploadView.as_view(), name="file_upload"),
    path("v1/my_bid", MyBid.as_view()),
    path("v1/my_bid/withdrawn/<int:tender_notice_id>", MyBid.as_view()),
    path("v1/tender_result", TenderResult.as_view()),
    path("v1/tender_award", TenderWorkAwardView.as_view()),
    path("v1/tender_boq_detail", TenderBOQDetailView.as_view()),
    path("v1/tender_attribute", TenderAttribute.as_view()),
    path("v1/bidder_bid_detail",BidderBidDetail.as_view()),
    path("v1/publisher_bank_detail", PublisherBankDetail.as_view()),
    path("v1/tender_bid_rejection",TenderBidRejection.as_view()),
    # path("v1/document_sample_file/<int:pk>",DocumentSampleFileView.as_view()),
    path("v1/document_sample_file",DocumentSampleFileView.as_view()),

]
