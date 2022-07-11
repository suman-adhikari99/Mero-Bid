
from django.contrib import admin

from .models import *
from utils.file_upload import get_file
from django.forms.models import model_to_dict
from django.core.files.storage import default_storage
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.contrib.admin.actions import delete_selected 


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    

    search_fields = ("email",)
    list_display = ("email","first_name", "last_name", "contact_no")
    
    actions = ['delete_selected']
    


    # def registration_front_document(self, obj):
    #     if obj.registration_certificate_front:
    #         return format_html('<a href={} ><img src="{}"  height="100" width="100"/></a>', obj.registration_certificate_front.url, obj.registration_certificate_front.url)

    # def registration_back_document(self, obj):
    #     if obj.registration_certificate_back:
    #         return format_html('<a href={} ><img src="{}"  height="100" width="100"/></a>', obj.registration_certificate_back.url, obj.registration_certificate_back.url)

    # def pan_vat_document(self, obj):
    #     if obj.pan_vat_certificate:
    #         return format_html('<a href={} ><img src="{}"  height="100" width="100"/></a>', obj.pan_vat_certificate.url, obj.pan_vat_certificate.url)

    # def liscense_front_document(self, obj):
    #     if obj.liscense_front:
    #         return format_html('<a href={} ><img src="{}"  height="100" width="100"/></a>', obj.liscense_front.url, obj.liscense_front.url)

    # def liscense_back_document(self, obj):
    #     if obj.liscense_back:
    #         return format_html('<a href={} ><img src="{}"  height="100" width="100"/></a>', obj.liscense_back.url, obj.liscense_back.url)
    

    # def has_delete_permission(self, request, obj=None):
    #     # Disable delete
    #     return False
    
    def delete_selected(modeladmin, request, queryset):
        for obj in queryset:
            
            if default_storage.exists(str(obj.registration_certificate_front)):
                default_storage.delete(str(obj.registration_certificate_front))
            if default_storage.exists(str(obj.registration_certificate_back)):
                default_storage.delete(str(obj.registration_certificate_back))
            if default_storage.exists(str(obj.pan_vat_certificate)):
                default_storage.delete(str(obj.pan_vat_certificate))
            if default_storage.exists(str(obj.liscense_front)):
                default_storage.delete(str(obj.liscense_front))
            if default_storage.exists(str(obj.liscense_back)):
                default_storage.delete(str(obj.liscense_back))
            # obj.delete()
        return delete_selected(modeladmin, request, queryset)


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")


class UserInterestAdmin(admin.ModelAdmin):
    # list_display = ("user_id",)
    list_display = ("user_id", "notice_id", "procument_id", "project_id")


admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(UserRole, UserRoleAdmin)
# admin.site.register(UserInterest, UserInterestAdmin)

admin.site.site_header = "Welcome back! 👋"

