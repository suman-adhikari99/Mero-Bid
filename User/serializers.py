
from rest_framework import serializers
from .models import *
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    pan_vat_certificate = serializers.SerializerMethodField(
        source='get_ pan_vat_certificate')
    registration_certificate_front = serializers.SerializerMethodField(
        source='get_registration_certificate_front')
    registration_certificate_back = serializers.SerializerMethodField(
        source='get_registration_certificate_back')
    liscense_front = serializers.SerializerMethodField(
        source='get_liscense_front')
    liscense_back = serializers.SerializerMethodField(
        source='get_liscense_back')

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name',  'contact_no', 'email', 'username', 'password', 'company_name', 'organization_category', 'office_email', 'website_url',
                  'province', 'district', 'municipality', 'company_contact_no', 'registration_certificate_front', 'registration_certificate_back', 'pan_vat_certificate', 'liscense_front', 'liscense_back']
        extra_kwargs = {
            "password": {'write_only': True}
        }

    def get_pan_vat_certificate(self, obj):
        if obj.pan_vat_certificate:
            return obj.pan_vat_certificate.url

    def get_registration_certificate_front(self, obj):
        if obj.registration_certificate_front:
            return obj.registration_certificate_front.url

    def get_registration_certificate_back(self, obj):
        if obj.registration_certificate_back:
            return obj.registration_certificate_back.url

    def get_liscense_back(self, obj):
        if obj.liscense_back:
            return obj.liscense_back.url

    def get_liscense_front(self, obj):
        if obj.liscense_front:
            return obj.liscense_front.url


class UserPostSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        required=True, validators=[validate_password])

    def validate(self, data):
        if self.context["role"] == 'Publisher':
            if not data.get('organization_category'):
                raise serializers.ValidationError(
                    {'organization_category': 'This field is required'})
        if data["contact_no"]:
            if not (10 <len(data["contact_no"])< 14):
                raise serializers.ValidationError(
                    {"contact_no": "This field's length should be between 11 to 13 "})
        if data["company_contact_no"]:
            if not (10 <len(data["company_contact_no"])< 14) :
                raise serializers.ValidationError(
                    {"company_contact_no": "This field's length should be between 11 to 13 "})
        return data

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'contact_no', 'email', 'username', 'password', 'company_name', 'organization_category', 'office_email', 'website_url',
                  'province', 'district', 'municipality', 'company_contact_no', 'registration_certificate_front', 'registration_certificate_back', 'pan_vat_certificate', 'liscense_front', 'liscense_back']
        extra_kwargs = {
            "password": {'write_only': True},
            "website_url": {"required": False}

        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInterest
        fields = '__all__'


class PersonalDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name',
                  'email', 'contact_no']
        extra_kwargs = {
            "middle_name": {"required": False}
        }


class OrganizationDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['company_name', 'organization_category', 'office_email', 'website_url', 'company_contact_no',
                  'province', 'district', 'municipality', 'registration_certificate_front', 'registration_certificate_back', 'pan_vat_certificate', 'liscense_front', 'liscense_back']
        extra_kwargs = {
            "website_url": {"required": False},
            "registration_certificate_front": {"required": False},
            "registration_certificate_back": {"required": False},
            "pan_vat_certificate": {"required": False},
            "liscense_back": {"required": False},
            "liscense_front": {"required": False},
        }

        def validate(self, data):
            if self.role.name == 'Publisher':
                if not data['organization_category']:
                    raise serializers.ValidationError(
                        {'Organization Category': 'Organization Category is required'})
            return data


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(
        required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
