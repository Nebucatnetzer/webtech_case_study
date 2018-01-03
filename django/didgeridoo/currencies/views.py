from django.shortcuts import render
from currencies.models import ExchangeRate, ExchangeRate_date, ExchangeRate_name
from currencies import exchange_rates


def currencies(request):
    # this function fetches the data from exchange_rates.py
    # evaluates if the values are already stored and
    # prepares the view all dynamicaly.
    # It can grow in terms of more Currencies over time automaticaly.
    raw_data, today = exchange_rates.get_exchange_rate()
    message_no = "Already querried today: "
    message_yes = " Updated successfully: "
    count_raw_data = 0
    for currency, rate in raw_data.items():
        count_raw_data += 1
        if ExchangeRate_date.objects.filter(date__date=today) \
                and ExchangeRate_name.objects.get(name=currency):
            message_no += currency + ", "
            # A: https://stackoverflow.com/a/27802801/4061870
        else:
            if ExchangeRate_date.objects.filter(date=today)[:1]:
                try:
                    date_dict = ExchangeRate_date.objects.filter(date=today).values()
                    date = date_dict[0]['date']
                    date_id = date_dict[0]['id']
                except Exception as e:
                    print('date_dict %s (%s)' % (e, type(e)))
            else:
                try:
                    exdate = ExchangeRate_date.objects.create(date=today)
                    exdate.save()
                except Exception as e:
                    print('exdate %s (%s)' % (e, type(e)))
            if ExchangeRate_name.objects.filter(name=currency)[:1]:
                try:
                    name_dict = ExchangeRate_name.objects.get(name=currency)
                    name = name_dict[0]['name']
                    name_id = name_dict[0]['id']
                except Exception as e:
                    print('exdate %s (%s)' % (e, type(e)))
            else:
                try:
                    exname = ExchangeRate_name.objects.create(name=currency)
                    exname.save()
                except Exception as e:
                    print('exname %s (%s)' % (e, type(e)))
            try:
                exrate = ExchangeRate.objects.create(
                    # name_id=name_id,
                    name_id=ExchangeRate_name.objects.only('id').get(name=currency).id,
                    # date_id=date_id,
                    date_id=ExchangeRate_date.objects.only('id').get(date=today).id,
                    exchange_rate_to_chf=rate,
                    )
                exrate.save()
                message_yes += currency + ", "

            except Exception as e:
                print('exrate %s (%s)' % (e, type(e)))

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
    currency_list = ExchangeRate.objects.all()
    # prepare data to be displayed in a html table:
    # https://stackoverflow.com/questions/8749158/removing-duplicates-from-dictionary#8749473
    # atomar_dates
    # A: https://stackoverflow.com/questions/37205793/django-values-list-vs-values#37205928
    # B: https://stackoverflow.com/questions/6521892/how-to-access-a-dictionary-key-value-present-inside-a-list
    # dates_list = ExchangeRate_date.objects.values_list('date', flat=True)
    # # atomar_currenies
    # currencies_list = ExchangeRate_name.objects.values_list('name', flat=True)
    # # search for currencies in a date and apend them to the list
    # currency_list = []
    # count_date = 0
    # count_currencies = 0
    # for date in dates_list:
    #     count_date += 1
    #     currency_dict = {}
    #     currency_dict['date'] = date
    #     for currency in currencies_list:
    #         count_currencies += 1
    #         try:
    #             temp = ExchangeRate.objects.objects.only('exchange_rate_to_chf').get(name=currency).id
    #             #temp = ExchangeRate.objects.filter(date=unique_date, name=currency).values()  # A
    #             exchange_rate_to_chf = temp[0]['exchange_rate_to_chf']
    #             currency_dict = currency_dict.update({currency: exchange_rate_to_chf})  # B
    #         except Exception as e:
    #             print('%s (%s)' % (e, type(e)))
    #     currency_list.append(currency_dict)
    #    assert False
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list,
                   'raw_data': raw_data,
                   'today': today,
                   # 'unique_dates_list': unique_dates_list,
                   # 'unique_currencies_list': unique_currencies_list,
                   'count_raw_data': count_raw_data,
                   # 'count_currencies': count_currencies,
                   # 'currency_dict': currency_dict,
                   'message': message})
