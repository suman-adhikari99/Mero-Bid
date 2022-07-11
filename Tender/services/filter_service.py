from User.models import User
from iteration_utilities import unique_everseen
from Tender.models import TenderNotice
from Tender.serializers import TenderNoticeSerializer
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT


# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

def filter_tenders(self, request, category):
    id = request.GET.get("id", None)
    qs = TenderNotice.objects.filter(category=category,deposit_paid=True).order_by("-created")
    organization_category = request.GET.get("organization_category", None)
    title = request.GET.get("title", None)
    district = request.GET.get("district", None)
    publishing_date = request.GET.get("publishing_date", None)
    procurement_type = request.GET.get("procurement_type", None)
    notice_category = request.GET.get("notice_category", None)
    project_category = request.GET.get("project_category", None)
    # filters
    if organization_category:
        user = User.objects.filter(organization_category=organization_category).values_list('id', flat=True)
        qs = TenderNotice.objects.filter(category=category, user__in=user).order_by("-created")
    if title:
        qs = qs.filter(title__icontains=title)
    if district:
        qs = qs.filter(district=district)
    if publishing_date:
        qs = qs.filter(publishing_date=publishing_date)
    if procurement_type:
        qs = qs.filter(procurement_type=procurement_type)
    if notice_category:
        qs = qs.filter(notice_category=notice_category)
    if id:
        qs = qs.filter(pk=id)
    if project_category:
        qs = qs.filter(project_category=project_category)
    # paginate tender notices
    pages = self.paginate_queryset(qs)
    # get all tender notice dates
    dates = []
    for page in pages:
        date = str(page.created.date())
        if date not in dates:
            dates.append(date)
    # get tender ids from pagination list object
    tender_ids = [page.id for page in pages]
    # filter tender notice with ids from pagination
    new_query_set = TenderNotice.objects.filter(id__in=tender_ids)
    tender_notice_dict = []
    for date in dates:
        qs_final = new_query_set.filter(created__startswith=date).order_by("-created")
        serializer = TenderNoticeSerializer(qs_final, many=True).data
        item_dict = {"date" :str(date) , "data":serializer}
        tender_notice_dict.append(item_dict)
    tender_notice_dict = list(unique_everseen(tender_notice_dict))

    # if len(pages) > 0:
    result = self.get_paginated_response(tender_notice_dict)
    data = result.data
    # else:
    #     serializer = self.get_serializer(tender_notice_dict)
    #     data = serializer.data
    return data