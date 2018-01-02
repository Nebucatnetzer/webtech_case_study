from django.shortcuts import render
from currencies.models import ExchangeRate
from currencies import exchange_rates


def currencies(request):
    # this function fetches the data from exchange_rates.py
    # evaluates if the values are already stored and
    # prepares the view all dynamicaly.
    # It can grow in terms of more Currencies over time automaticaly.
    raw_data, today = exchange_rates.get_exchange_rate()
    message_no = "Already querried today: "
    message_yes = " Updated successfully: "
    for currency, rate in raw_data.items():
        if ExchangeRate.objects.filter(date=today, name=currency)[:1]:
            message_no += currency + ", "
        else:
            e = ExchangeRate.objects.create(
                name=currency,
                exchange_rate_to_chf=rate,
                date=today
                )
            e.save()
            message_yes += currency + ", "

    # prepare messages:
    message_no = message_no[::-1]  # invert the string
    message_no = message_no.replace(",", "!", 1)  # replace first , with !
    message_no = message_no[::-1]  # invert the string back
    message_yes = message_yes[::-1]  # invert the string
    message_yes = message_yes.replace(",", "!", 1)  # replace first , with !
    message_yes = message_yes[::-1]  # invert the string back

    if len(message_no) > 24 and len(message_yes) > 23:
        message = message_no + message_yes
    elif len(message_no) > 24:
        message = message_no
    elif len(message_yes) > 23:
        message = message_yes
    else:
        message = "something whent wrong"

    # prepare data to be displayed in a html table:
    # https://stackoverflow.com/questions/8749158/removing-duplicates-from-dictionary#8749473
    # atomar_dates
    # A: https://stackoverflow.com/questions/37205793/django-values-list-vs-values#37205928
    # B: https://stackoverflow.com/questions/6521892/how-to-access-a-dictionary-key-value-present-inside-a-list
    unique_dates_list = ExchangeRate.objects.values_list('date', flat=True).distinct()
    # atomar_currenies
    unique_currencies_list = ExchangeRate.objects.values_list('name', flat=True).distinct()
    # search for currencies in a date and apend them to the list
    currency_list = []
    count_date = 0
    count_currencies = 0
    for unique_date in unique_dates_list:
        count_date += 1
        currency_dict = {}
        currency_dict['date'] = unique_date
        for unique_currency in unique_currencies_list:
            count_currencies += 1
            try:
                temp = ExchangeRate.objects.filter(date=unique_date, name=unique_currency).values()  #A
                exchange_rate_to_chf = temp[0]['exchange_rate_to_chf']
                currency_dict = currency_dict.update({unique_currency: exchange_rate_to_chf})  #B
            except Exception as e:
                print('%s (%s)' % (e, type(e)))
        currency_list.append(currency_dict)
        assert False
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list,
                   'raw_data': raw_data,
                   'today': today,
                   'unique_dates_list': unique_dates_list,
                   'unique_currencies_list': unique_currencies_list,
                   'count_date': count_date,
                   'count_currencies': count_currencies,
                   'currency_dict': currency_dict,
                   'message': message})
