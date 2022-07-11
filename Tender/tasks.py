from utils.email import SendEmail
def tender_change_mail(email_of_bidder,title):
    body = 'See The Changes of Tender That You Have Bid ',
    data = {
    'subject' : 'Changes on Tender   - MeroBid',
    'body' : str(body),
    'to' : email_of_bidder,
    'title':title,
    'html_template':'tender_change_mail.html'
    }
    SendEmail.send_mass_email(data)