from .models import Setting
from ledger.models import Document, Category, Account, Transaction, Entry, Closing
from icecream import ic
from django.db.models import Sum, Q
from django.db import transaction as trans
from django.db import DatabaseError 
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ledger import utils

def close(yr):

    start_dt = yr.start_date.strftime("%Y-%m-%d")
    end_dt = yr.end_date.strftime("%Y-%m-%d")
    ref = utils.generate_trans_number(end_dt)
    document = get_object_or_404(Document, pk=1)
    suspense_setting = Setting.objects.filter(name__iexact='suspense').first().value
    suspense = get_object_or_404(Account, pk=suspense_setting)

    account_balances = Account.objects.filter(
        Q(account_number__startswith='4') | Q(account_number__startswith='5')
    ).filter(
        entry__transaction__date__range=(start_dt, end_dt)
    ).annotate(
        total=Sum('entry__debit') - Sum('entry__credit')
    ).values('id', 'name', 'total')

    account_balances_bs = Account.objects.filter(
        Q(account_number__startswith='1') | Q(account_number__startswith='2') | Q(account_number__startswith='3')
    ).filter(
        entry__transaction__date__range=(start_dt, end_dt)
    ).annotate(
        total=Sum('entry__debit') - Sum('entry__credit')
    ).values('id', 'name', 'total')

    # ic(account_balances)

    try:
        with trans.atomic():
            g_total = 0
            for balance in account_balances:
                g_total = g_total + balance['total']
                account = get_object_or_404(Account, pk=balance['id'])
                closing = Closing(year=yr, account=account, pre=1, amount=balance['total'])
                closing.save()
            for balance in account_balances_bs:
                account = get_object_or_404(Account, pk=balance['id'])
                closing = Closing(year=yr, account=account, pre=1, amount=balance['total'])
                closing.save()
            ic(g_total)
            transaction = Transaction(ref=ref, date=end_dt, document=document, year=yr, description="Closing Balance")
            transaction.save()
            for balance in account_balances:
                account = get_object_or_404(Account, pk=balance['id'])
                if balance['total'] > 0:
                    entry =Entry(transaction=transaction, account=account, debit=0, credit=abs(balance['total']))
                    entry.save()
                else:
                    entry =Entry(transaction=transaction, account=account, debit=abs(balance['total']), credit=0)
                    entry.save()
            if g_total > 0:
                entry =Entry(transaction=transaction, account=suspense, debit=abs(g_total), credit=0)
                entry.save()
            else:
                entry =Entry(transaction=transaction, account=suspense, debit=0, credit=abs(g_total))
                entry.save()
            for balance in account_balances:
                account = get_object_or_404(Account, pk=balance['id'])
                closing = Closing(year=yr, account=account, pre=0, amount=0)
                closing.save()
            for balance in account_balances_bs:
                account = get_object_or_404(Account, pk=balance['id'])
                if account.id == suspense.id:
                    closing = Closing(year=yr, account=account, pre=0, amount=g_total)
                    closing.save()
                else:
                    closing = Closing(year=yr, account=account, pre=0, amount=balance['total'])
                    closing.save()

    except (DatabaseError) as e:
        ic(e)
        return JsonResponse({'errors':e.message_dict}, safe=False)

    str1 = "Year closed!"
    return str1