from celery.decorators import task
from celery.utils.log import get_task_logger
from utils.email import SendEmail
logger = get_task_logger(__name__)

                        
@task(name='account_verification_mail')
def account_verification_mail(email, full_name,link):
    body = 'Click Following Link to Verify Your User Accounts '+ link,
    data = {
        'subject' : 'User Account Verification - MeroBid',
        'body' : str(body),
        'to' : email,
        'user_name': full_name,
        'link' : link,
        'html_template' : 'email/account_verification.html'
    }
    SendEmail.send_email(data)

@task(name='password_reset_mail')
def password_reset_mail(email, full_name,link):
    body = 'Click Following Link to Reset Your Password '+ link,
    data = {
            'subject' : 'Password Reset - MeroBid',
            'body' : str(body),
            'to' : email,
            'user_name': full_name,
            'link' : link,
            'html_template' : 'email/password_reset.html'
        }
    SendEmail.send_email(data)    