from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from decorator.auth_decorator import auth_required
from e_bidding.api_render import api_response_render
from .serializers import *
from User.models import User, UserRole
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse
from .tasks import account_verification_mail, password_reset_mail
from utils.expirey_date_for_cookie import *
from datetime import datetime
import uuid
# register user
class RegisterView(APIView):
    
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                data["username"] =data.get('email')
                serializer = UserPostSerializer(data=data,context={'role': data.get("role")})
                if serializer.is_valid():
                    serializer.save()
                    role_name = data.get("role")
                    user = User.objects.last()
                    
                    if role_name == 'Publisher':
                        role = Role.objects.filter(name='Publisher').first() 
                    else:
                        role = Role.objects.filter(name='Bidder').first()
                    if role is None:
                            return api_response_render(status_msg=f"{role_name} doesn't exist", status_type='Error', status_code=400)        
                    UserRole.objects.create(user=user, role=role)

                    # register verification email send
                    uuid = user.email_verification_token
                    if uuid:
                        # link = reverse('users:user_registration_verification', args=[uuid] , request=request)
                        link = f"https://ebidding.axiossoftworks.com/user/registration_verification/{uuid}"
                        # send Email
                        account_verification_mail.delay(user.email, user.full_name,link)
                    return api_response_render(status_msg=f"Register Confirmation mail has been sent. Please check your mail {user.email}", status_type='Success', status_code=200)
                return api_response_render(status_msg=serializer.errors, status_type='Error', status_code=400)    
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

    
class RegistrationVerificationView(APIView):

        def get(self,request,token):
            try:
                user = User.check_user_email_token(token)
                if not user.email_verification:
                    user.email_verification = True
                    user.email_verification_token = None
                    user.save()
                    return api_response_render(status_msg="Account Verified.", status_type='Success', status_code=200)
                return api_response_render(status_msg="This Account is already verified", status_type='Success', status_code=201)
            except NotFound as e:
                return api_response_render(status_msg=str(e), status_type='Error', status_code=400)
            except Exception as e:
                return api_response_render(status_msg=str(e), status_type='Error', status_code=500) 


# password reset  
class SendPasswordResetEmailView(APIView):
    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
             raise NotFound("User Doesn't Exist")

    def post(self, request):
        try:
            serializer = SendPasswordResetEmailSerializer(data=request.data)
            if serializer.is_valid():
                user = self.get_user(serializer.data['email'])
                password_reset_token = uuid.uuid4()
                user.password_reset_token = password_reset_token
                user.save()
                # link = reverse('users:user-password-reset', args=[user.email_verification_token] , request=request)
                link = f"https://ebidding.axiossoftworks.com/user/password_reset/{password_reset_token}"
                # send Email
                password_reset_mail.delay(user.email, user.full_name,link)
                return api_response_render(data=serializer.data, status_msg=f"Password Reset Link has been send in your email. Please check your email {user.email}", status_type='Success', status_code=200)
            return api_response_render(status_msg=serializer.errors, status_type='Error', status_code=400)
        except NotFound as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)

class PasswordResetUpdateView(APIView):
    
    def put(self, request, token):
        try:
            user = User.check_user_password_reset_token(token)
            serializer = ResetPasswordSerializer(data=request.data)
            if serializer.is_valid():
                if serializer.data.get("password") != serializer.data.get("confirm_password"):
                    return api_response_render(status_msg="Password fields didn't match.", status_type='Error', status_code=400)
                user.set_password(serializer.data.get("password"))
                user.password_reset_token = None
                user.save()
                return api_response_render(status_msg="Password changed successfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=serializer.errors, status_type='Error', status_code=400)
        except NotFound as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400)
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)  
        

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
class LoginView(APIView):

    def get(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if raw_token is None:
            return api_response_render(status_msg='User Session Expired', status_type='Error', status_code=403)
        user = User.user_from_token(raw_token)
        user_role = UserRole.objects.get(user_id=user['user_id']).role.name
        return api_response_render(data = {"role": user_role},status_msg="User Session Exist", status_type='Success', status_code=200)

    def post(self, request):
        data = request.data
        response = Response()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)
        remember_me=request.data.get('remember_me',None)
        if user is not None:
            if user.is_active and user.email_verification:
                data = get_tokens_for_user(user)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["access"],
                    expires=expirey_days(3) if remember_me else expirey_hours(3),
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                )
                user.last_login=datetime.now()
                user.save()
                role = UserRole.objects.filter(
                    user=user).first().role.name
                csrf.get_token(request)
                response.data = {"Success" : "Login successful","data":data,"role":role}
                return response
            return api_response_render(status_msg=f"This account is not verified. Please check your email {user.email}!!", status_type='Error', status_code=400)
        else:
            return api_response_render(status_msg="Invalid username or password!!", status_type='Error', status_code=400)

    def delete(self, request):
        response = Response()
        response.delete_cookie('access_token')
        response.data = {"message" : "User Session Deletion"}
        return response 


class UserView(APIView):

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
             raise NotFound("User Doesn't Exist")

    @auth_required()
    def get(self, request, user_id):
        try:
            user = self.get_user(user_id)
            serialized_user = UserSerializer(user)
            return api_response_render(data=serialized_user.data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)
        except NotFound as e: 
             return api_response_render(status_msg=str(e), status_type='Error', status_code=400)    

class UserInterestView(APIView):
    @auth_required()
    def post(self, request, user_id):
        data = request.data
        data['user_id'] = user_id

        serializers = UserInterestSerializer(data=data)
        serializers.is_valid(raise_exception=True)
        if serializers.save():
            return api_response_render(data=serializers.data, status_msg="Data Store Sucessfully", status_type='Success', status_code=200)
        return api_response_render(status_msg=serializers.errors, status_type='Error', status_code=422)

    def get_user_interest(self, pk):
        try:
            return UserInterest.objects.get(pk=pk)
        except UserInterest.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk == None:
            user_interest = UserInterest.objects.all()
            stat = True
        else:
            user_interest = self.get_user_interest(pk)
            stat = False
        serialized_user_interest = UserInterestSerializer(
            user_interest, many=stat)
        return api_response_render(data=serialized_user_interest.data, status_msg="Data Fetch Sucessfully", status_type='Success', status_code=200)

    @auth_required()
    def put(self, request, user_id, pk):
        user_interest = self.get_user_interest(pk)
        data = request.data
        data['user_id'] = user_id
        serialized_user_interest = UserInterestSerializer(user_interest, data)
        if serialized_user_interest.is_valid():
            serialized_user_interest.save()
            return api_response_render(data=serialized_user_interest.data, status_msg="Data updated Sucessfully", status_type='Success', status_code=200)
        return api_response_render(status_msg=serialized_user_interest.errors, status_type='Error', status_code=400)

    @auth_required()
    def delete(self, request, user_id):
        user_interest = self.get_user_interest(user_id)
        user_interest.delete()
        return api_response_render(status_msg="Data Deleted Sucessfully", status_type='Success', status_code=204)


class PersonalDetailsView(APIView):

    @auth_required()
    def put(self, request, user_id):
        try:
            user = UserView.get_user(self,user_id)
            serialized_user = PersonalDetailsViewSerializer(
                user, data=request.data)
            if serialized_user.is_valid(raise_exception=True):
                serialized_user.save()
                return api_response_render(data=serialized_user.data, status_msg="Personal Detail Updated Sucessfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=serialized_user.errors, status_type='Error', status_code=400)
        except NotFound as e: 
             return api_response_render(status_msg=str(e), status_type='Error', status_code=400)   
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)


class OrganizationDetailsView(APIView):

    @auth_required()
    def put(self, request, user_id):
        try:
            user = UserView.get_user(self,user_id)
            serialized_user = OrganizationDetailsViewSerializer(
                user, data=request.data)
            if serialized_user.is_valid(raise_exception=True):
                serialized_user.save()
                return api_response_render(data=serialized_user.data, status_msg="Organization Detail Updated Sucessfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=serialized_user.errors, status_type='Error', status_code=400)
        except NotFound as e: 
             return api_response_render(status_msg=str(e), status_type='Error', status_code=400)       
        except Exception as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=500)   

class ChangePasswordView(APIView):
  
    @auth_required()
    def post(self, request, user_id):
        try:
            user = UserView.get_user(self,user_id)
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                if not user.check_password(serializer.data.get("old_password")):
                    return api_response_render(status_msg="Wrong Old Password", status_type='Error', status_code=400) 
                if serializer.data.get("password") != serializer.data.get("confirm_password"):
                    return api_response_render(status_msg="Password fields didn't match.", status_type='Error', status_code=400)
                user.set_password(serializer.data.get("password"))
                user.save()
                return api_response_render(status_msg="Password changed successfully", status_type='Success', status_code=200)
            return api_response_render(status_msg=serializer.errors, status_type='Error', status_code=400)
        except NotFound as e:
            return api_response_render(status_msg=str(e), status_type='Error', status_code=400) 
 
