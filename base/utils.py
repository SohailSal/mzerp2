from .models import Setting, Year
from ledger.models import Document, Category, Account, Transaction, Entry, Closing
from icecream import ic
from django.db.models import Sum, Q, F
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
    retained_setting = Setting.objects.filter(name__iexact='retained').first().value
    retained = get_object_or_404(Account, pk=retained_setting)
    prev_yr = Year.objects.filter(id=yr.previous).first()

    account_balances = Account.objects.filter(
        Q(account_number__startswith='4') | Q(account_number__startswith='5')
    ).filter(
        entry__transaction__date__range=(start_dt, end_dt)
    ).annotate(
        total=Sum('entry__debit') - Sum('entry__credit'),
        amount=Sum('entry__debit') - Sum('entry__credit'),
        acc = F('id')
    ).values('id', 'acc', 'name', 'total', 'amount', 'category')

    account_balances_bs = Account.objects.filter(
        Q(account_number__startswith='1') | Q(account_number__startswith='2') | Q(account_number__startswith='3')
    ).filter(
        entry__transaction__date__range=(start_dt, end_dt)
    ).annotate(
        total=Sum('entry__debit') - Sum('entry__credit'),
        amount=Sum('entry__debit') - Sum('entry__credit'),
        acc = F('id')
    ).values('id', 'acc', 'name', 'total', 'amount', 'category')

    combined = account_balances | account_balances_bs
    # ic(combined)

    closings = None
    uncommon_openings = None
    uncommon_new = None
    merged_data = []
    if (yr.previous > 0) and (prev_yr.closed):
        closings = Closing.objects.filter(year = yr.previous).filter(pre = 0).filter(
            Q(account__account_number__startswith='1') | Q(account__account_number__startswith='2') | Q(account__account_number__startswith='3')
        ).annotate(
            name = F('account__name'),
            acc = F('account'),
            category = F('account__category__id')
        ).values('acc','name','amount','category')
        # ic(closings)
        uncommon_openings = closings.exclude(account__in=account_balances_bs.values('id')).values('acc','name','amount','category')
        uncommon_new = account_balances_bs.exclude(id__in=closings.values('account')).values('acc','name','amount','category')
        # uncommon_new = combined.exclude(id__in=closings.values('account')).values('acc','name','amount','category')

        for data1 in combined:
            for data2 in closings:
                if data1['id'] == data2['acc']:
                    merged_data.append({
                        'acc': data1['id'],
                        'name': data1['name'],
                        'amount': data1['amount'] + data2['amount'],
                        'category': data1['category']
                    })

    result = merged_data + list(uncommon_openings) + list(uncommon_new)
    # ic(result)
    # ic(account_balances)
    try:
        with trans.atomic():
            g_total = 0
            for balance in account_balances:
                g_total = g_total + balance['total']
                account = get_object_or_404(Account, pk=balance['id'])
                closing = Closing(year=yr, account=account, pre=1, amount=balance['total'])
                closing.save()
            for balance in result:
                account = get_object_or_404(Account, pk=balance['acc'])
                closing = Closing(year=yr, account=account, pre=1, amount=balance['amount'])
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
                entry =Entry(transaction=transaction, account=retained, debit=abs(g_total), credit=0)
                entry.save()
            else:
                entry =Entry(transaction=transaction, account=retained, debit=0, credit=abs(g_total))
                entry.save()
            for balance in account_balances:
                account = get_object_or_404(Account, pk=balance['id'])
                closing = Closing(year=yr, account=account, pre=0, amount=0)
                closing.save()
            for balance in result:
                account = get_object_or_404(Account, pk=balance['acc'])
                if account == retained:
                    ob = get_object_or_404(Closing, year = yr.previous, pre = 0, account = retained)
                    closing = Closing(year=yr, account=account, pre=0, amount=ob.amount+g_total)
                    closing.save()
                else:
                    closing = Closing(year=yr, account=account, pre=0, amount=balance['amount'])
                    closing.save()
            # closing = Closing(year=yr, account=retained, pre=0, amount=g_total)
            # closing.save()
            yr.closed = True
            yr.save()

    except (DatabaseError) as e:
        ic(e)
        return JsonResponse({'errors':e.message_dict}, safe=False)

    str1 = "Year closed!"
    return str1
