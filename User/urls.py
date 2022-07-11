from django.urls import path

from User.views import RegisterView, LoginView, UserView, UserInterestView, PersonalDetailsView, OrganizationDetailsView,RegistrationVerificationView, SendPasswordResetEmailView, PasswordResetUpdateView, ChangePasswordView
from django.conf import settings
from django.conf.urls.static import static


app_name="User"
urlpatterns=[
    path('v1/register',RegisterView.as_view()),
    path('v1/login', LoginView.as_view()),
    path('v1/user_session', LoginView.as_view()),
    path('v1/user_interest',UserInterestView.as_view()),
    path('v1/user_interest/<int:pk>', UserInterestView.as_view()),
    path('v1/user',UserView.as_view()),
    path('v1/user/personal_detail',PersonalDetailsView.as_view()),
    path('v1/user/organization_detail',OrganizationDetailsView.as_view()),
    # change password by logged user
    path('v1/user/change_password',ChangePasswordView.as_view()),
    # user registration verification 
    path('v1/user/registration_verification/<token>/',RegistrationVerificationView.as_view(), name='user_registration_verification'),
    
    # password reset
    path('v1/user/send_reset_password_email/', SendPasswordResetEmailView.as_view(), name='user-send-reset-password-email'),
    path('v1/user/password_reset/<token>/', PasswordResetUpdateView.as_view(), name='user-password-reset'),

    

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)




#celery -A your_project_name worker -l info