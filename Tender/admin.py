from unittest import result
from django.contrib import admin
from .models import *
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from utils.file_register import register_files


class TenderWorkAwardAdmin(admin.ModelAdmin):
    

    def user_company_name(self, obj):
        
        return obj.tender_awarded_user.company_name + ' [ ' + obj.tender_awarded_user.company_contact_no+ ' ]'

    def user_name(self, obj):
        user_name = obj.tender_awarded_user.full_name + ' [ ' + obj.tender_awarded_user.contact_no+ ' ]'
        link=reverse("admin:User_user_change", args=[obj.tender_awarded_user.id]) #model name has to be lowercase
        return format_html('<a href={} target="_blank">{}</a>', link, user_name)
    

    list_display = ('work_awarded','tender_notice','tender_number', 'price', 'user_company_name', 'user_name')

class TenderNoticeAdmin(admin.ModelAdmin):
    

    def user_company_name(self, obj):
        return obj.user.company_name + ' [ ' + obj.user.company_contact_no+ ' ]'

    def user_name(self, obj):
        user_name = obj.user.full_name + ' [ ' + obj.user.contact_no+ ' ]'
        link=reverse("admin:User_user_change", args=[obj.user.id]) #model name has to be lowercase
        return format_html('<a href={} target="_blank">{}</a>', link, user_name)

    
    def deposit_paid(self, obj):
        result = "Unpaid"
        badge_class = "danger"
        if obj.deposit_paid == True:
            result = "Paid"
            badge_class = "success"
        return format_html('<span class="badge badge-{0} text-center">{1}<span>', badge_class, result )

    def deposit_refunded(self, obj):
        result = "NO"
        badge_class = "danger"
        if obj.deposit_refunded == True:
            result = "Yes"
            badge_class = "success"
        return format_html('<span class="badge badge-{0} text-center">{1}<span>', badge_class, result )

    list_display = ('tender_number', 'title', 'category', 'user_name','user_company_name', 'deposit_paid', 'deposit_refunded')
    list_filter =('category','deposit_paid','deposit_refunded')
    actions = ['update_deposit_refunded']

   
    def update_deposit_refunded(modeladmin, request, queryset):
        for obj in queryset:
            tender_notice = TenderNotice.objects.get(id=obj.id)
            if tender_notice:
                if obj.deposit_refunded == False:
                    tender_notice.deposit_refunded = True
                tender_notice.save()
                messages.add_message(request, messages.SUCCESS, 'Deposit Refundable Has Been Successfully Updated')
                return True

class DocumentSampleFileAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if request.FILES:
            request.data={key:value for key, value in request.FILES.items()}
            register_files(request)
        super().save_model(request, obj, form, change)
        
# Register your models here.
admin.site.register(NoticeCategory)
admin.site.register(ProcurementType)
admin.site.register(ProjectCategory)
admin.site.register(TenderNotice, TenderNoticeAdmin)
# admin.site.register(TenderBOQ)
# admin.site.register(TenderBOQDetail)
admin.site.register(TenderBid)
# admin.site.register(TenderPrice)
admin.site.register(TenderWorkAward, TenderWorkAwardAdmin)
admin.site.register(DocumentSampleFile,DocumentSampleFileAdmin)