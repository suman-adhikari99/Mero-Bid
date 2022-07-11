from django.core.mail import send_mail
import os
from django.template.loader import render_to_string
from django.core.mail import get_connection, EmailMultiAlternatives

class SendEmail:
    @staticmethod
    def send_email(data):
       
       send_mail(
            data['subject'],
            data['body'],
            os.environ.get('EMAIL_FROM'),
            [data['to']],
            fail_silently=False,
            html_message = render_to_string(data['html_template'], {'email': data['to'], 'url': data['link'], 'user_name': data["user_name"]})
        )

    @staticmethod
    def send_mass_email(data):
        connection = get_connection()
        connection.open() 
        html_content = render_to_string(data['html_template'], { 'title': data['title'] })              
        text_content = "..."                      
        msg = EmailMultiAlternatives("subject", text_content,os.environ.get('EMAIL_FROM'),data['to'], connection=connection)                                      
        msg.attach_alternative(html_content, "text/html")                                                                                                                                                                               
        msg.send() 
        connection.close() 
