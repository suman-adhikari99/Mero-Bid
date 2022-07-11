from User.models import Role, UserRole
from Transactions.models import TransactionMain
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, ExtractMonth
import calendar


def dashboard(request):
    # transaction = TransactionMain.objects.filter().values('created').order_by('created')
    # transaction = TransactionMain.objects.filter().values('created').order_by('created').annotate(sum=Sum('amount')).group_by('created')

    # transactions = (TransactionMain.objects
    # # .annotate(month=TruncMonth('created'))
    # .values('tender_notice_id')
    # .annotate(dcount=Count('tender_notice_id')))

    # transactions = TransactionMain.objects.filter().annotate(month=TruncMonth('created')).values(month=ExtractMonth('month')).annotate(count=Count('id')).order_by('month')
    transactions = TransactionMain.objects.filter(fee_for="Bid").annotate(month=TruncMonth('created')).values(month=ExtractMonth('month')).annotate(amount=Sum('amount')).order_by('month')

    
    role = Role.objects.all()
    role_count = []
    role_name = []

    for r in role:
        count = UserRole.objects.filter(role_id=r.id).count()
        role_name.append(r.name)
        role_count.append(count)
    month_name = []
    transaction_amount = []
    for transaction in transactions:
        month_name.append(calendar.month_name[transaction['month']])
        transaction_amount.append(transaction['amount'])
    
    return {'role_name': role_name, 'role_count':role_count, 'month_name': month_name, 'transaction_amount': transaction_amount }