import imp
from django.contrib import admin
from .models import Ledger, TransactionMain, BidFee
from .forms import LedgerAdminForm
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from Tender.models import TenderNotice
import django_tables2 as tables
# Register your models here.


class TransactionMainTable(tables.Table):
    class Meta:
        model = TransactionMain
        template_name = "django_tables2/bootstrap.html"
        fields = ("user","amount" ,"payment_type","payment_method","status","tender_notice")

class TenderNoticeTable(tables.Table):
    class Meta:
        model = TenderNotice
        template_name = "django_tables2/bootstrap.html"
        fields = ("tender_number","user", "title","submission_date","publishing_date")

class CustomAdmin(admin.AdminSite):
    def get_urls(
        self,
    ):
        return [
            path(
                "transaction_main_page/",
                self.admin_view(self.transaction_main_page),
                name="transaction_main_page",
            ),
            path(
                "tender_notice_page/",
                self.admin_view(self.tender_noitce_page),
                name="tender_notice_page",
            ),
        ] + super().get_urls()

    def transaction_main_page(self, request):
        transaction_main=TransactionMain.objects.all()
        date_only=set([d.created.date() for d in transaction_main ])
        context = {
            'data':{date_only:TransactionMainTable(transaction_main.filter(created__date=date_only)) for date_only in date_only },
            "app_list": self.get_app_list(request),
            **self.each_context(request),
        }

        return TemplateResponse(request, "admin/admin_custom_table.html", context)
        
    def tender_noitce_page(self, request):
        tender_noitce=TenderNotice.objects.all()
        date_only=set([d.created.date() for d in tender_noitce ])
        context = {
            'data':{date_only:TenderNoticeTable(tender_noitce.filter(created__date=date_only)) for date_only in date_only },
            "app_list": self.get_app_list(request),
            **self.each_context(request),
        }
        return TemplateResponse(request, "admin/admin_custom_table.html", context)

admin.site.__class__ = CustomAdmin


class LedgerAdmin(admin.ModelAdmin):
    form = LedgerAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'ledger_head', 'has_sub_code', 'groupcode'),
        }),
    )
    readonly_fields = ('groupcode',)

class TransactionMainAdmin(admin.ModelAdmin):

    def user_company_name(self, obj):
        return obj.user.company_name + ' [ ' + obj.user.company_contact_no+ ' ]'

    def user_name(self, obj):
        user_name = obj.user.full_name + ' [ ' + obj.user.contact_no+ ' ]'
        link=reverse("admin:User_user_change", args=[obj.user.id]) #model name has to be lowercase
        return format_html('<a href={} target="_blank">{}</a>', link, user_name)

    list_display = ("id","description","user_name", "user_company_name", "payment_method", "payment_type", "amount", "fee_for","status") 
    list_filter =('payment_method','status','payment_type')
class TemplateAdmin(admin.ModelAdmin):
    ...
    change_form_template = 'admin/preview_template.html'
    

admin.site.register(Ledger, LedgerAdmin)

admin.site.register(TransactionMain, TransactionMainAdmin)

admin.site.register(BidFee)

