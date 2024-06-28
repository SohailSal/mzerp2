from ledger.models import Category, Account, Entry, Closing
from icecream import ic

def close(yr):

    # year_setting = Setting.objects.filter(name__iexact='year').first().value
    # year = get_object_or_404(Year, pk=year_setting)
    # start_dt = year.start_date.strftime("%Y-%m-%d")
    # # ic(start_dt)
    # # ic(dt)
    # account_balances = Account.objects.filter(
    #     entry__transaction__date__range=(start_dt, dt)
    # ).annotate(
    #     total=Sum('entry__debit') - Sum('entry__credit')
    # ).values('name', 'total')


    ic('hello world')
    str1 = yr
    return str1