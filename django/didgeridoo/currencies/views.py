from django.shortcuts import render
import datetime
from currencies.models import (ExchangeRate,
                               ExchangeRate_date,
                               ExchangeRate_name)
from currencies import exchange_rates


def currencies(request):
    # this function fetches the data from exchange_rates.py
    # evaluates if the values are already stored and
    # prepares the view all dynamicaly.
    # It can grow in terms of more Currencies over time automaticaly.
    # try:
    today = ''
    raw_data = ''
    raw_data, today = exchange_rates.get_exchange_rate()
    # except Exception as e:
    #     print('get_exchange_rate() %s (%s) on %s'
    #           % (e, type(e), today))
    message_no = "Already querried today: "
    message_yes = " Updated successfully: "
    count_raw_data = 0
    if raw_data != "SNB did not update the currencies for today.":
        for currency, rate in raw_data.items():
            count_raw_data += 1
            if ExchangeRate.objects.filter(
                    date__date=today,
                    name__name=currency):
                message_no += currency + ", "
            # A: https://stackoverflow.com/a/27802801/4061870
            else:
                if ExchangeRate_date.objects.filter(date=today)[:1]:
                    try:
                        # lustigerweise gibt .values() den value und den id
                        # zurück. Ohne .values() gibts nur den "value"
                        date_dict = ExchangeRate_date.objects.filter(
                            date=today).values()
                        date = date_dict[0]['date']
                        date_id = date_dict[0]['id']
                    except Exception as e:
                        print('exdate_exists %s (%s) on %s'
                              % (e, type(e), today))
                else:
                    try:
                        exdate = ExchangeRate_date.objects.create(
                            date=today)
                        exdate.save()
                    except Exception as e:
                        print('exdate_not_exists %s (%s) for %s'
                              % (e, type(e), today))
                if ExchangeRate_name.objects.filter(
                        name=currency)[:1]:
                    try:
                        name_dict = ExchangeRate_name.objects.filter(
                            name=currency).values()
                        name = name_dict[0]['name']
                        name_id = name_dict[0]['id']
                    except Exception as e:
                        print('exname_exists %s (%s) on %s'
                              % (e, type(e), currency))
                else:
                    try:
                        exname = ExchangeRate_name.objects.create(
                            name=currency)
                        exname.save()
                    except Exception as e:
                        print('exname_not_exists %s (%s) on %s'
                              % (e, type(e), currency))
                try:
                    exrate = ExchangeRate.objects.create(
                        # name_id=name_id,
                        name_id=ExchangeRate_name.objects.get(
                            name=currency).id,
                        # date_id=date_id,
                        date_id=ExchangeRate_date.objects.get(
                            date=today).id,
                        exchange_rate_to_chf=rate,
                        )
                    exrate.save()
                    message_yes += currency + ", "

                except Exception as e:
                    print('exrate_create %s (%s) on %s for %s'
                          % (e, type(e), currency, today))

        # prepare messages:
        message_no = message_no[::-1]  # invert the string
        message_no = message_no.replace(",", "!", 1)  # replace first , with !
        message_no = message_no[::-1]  # invert the string back
        message_yes = message_yes[::-1]  # invert the string
        message_yes = message_yes.replace(",", "!", 1)  # replace f. , with !
        message_yes = message_yes[::-1]  # invert the string back

        if len(message_no) > 24 and len(message_yes) > 23:
            message = message_no + message_yes
        elif len(message_no) > 24:
            message = message_no
        elif len(message_yes) > 23:
            message = message_yes
        elif datetime.datetime.today().isoweekday() == 6:
            message = """Die Abfrage wurde ohne ergebniss beendet.
            Es ist Samstag, die SNB publiziert nur an Arbeitstagen
            neue Kurse...
            """
        elif datetime.datetime.today().isoweekday() == 7:
            message = """Die Abfrage wurde ohne ergebniss beendet.
            Es ist Sonntag, die SNB publiziert nur an Arbeitstagen
            neue Kurse...
            """
        else:
            message = """Die Abfrage wurde ohne ergebniss beendet.
            Kann es sein dass die SNB aufgrund eines Feiertages
            geschlossen ist?
            """
    else:
        message = "Die SNB hat die Währungsliste noch nicht aktualisiert."
    currency_list = ExchangeRate.objects.all()
    currency_USD_list = ExchangeRate.objects.filter(name__name='USD')
    currency_EUR_list = ExchangeRate.objects.filter(name__name='EUR')
    currency_JPY_list = ExchangeRate.objects.filter(name__name='JPY')
    currency_GBP_list = ExchangeRate.objects.filter(name__name='GBP')
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # I leave this part in the document as history.
    # Problem is that i get the expected List with dictionaries like:
    #  view_currencies_list[
    # {'date': '2017-12-29, 'USD':'1.00', 'EUR':'1.00', 'GBP':'1.00', 'JPY':'1.00'},
    # {'date': '2017-12-30, 'USD':'1.00', 'EUR':'1.00', 'GBP':'1.00', 'JPY':'1.00'},
    # ]
    # but the dict of 'date:' does not seam to deliver the same values as
    # the dict's of key name:'USD' im not able to fix this in moment.
    # nor am i able to generate a HTML table with date | USD | EUR | ...
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # prepare data to be displayed in a html table:
    # https://stackoverflow.com/questions/8749158/removing-duplicates-from-dictionary#8749473
    # A: https://stackoverflow.com/questions/37205793/django-values-list-vs-values#37205928
    # B: https://stackoverflow.com/questions/6521892/how-to-access-a-dictionary-key-value-present-inside-a-list
    # # search for currencies in a date and apend them to the list
    # view_currency_list = []
    # view_currencies_list = ExchangeRate_name.objects.all()
    # view_dates_list = ExchangeRate_date.objects.all()
    # count_date = 0
    # count_currencies = 0
    # for view_date in view_dates_list:
    #     count_date += 1
    #     view_currency_dict = {view_date}
    #     # view_currency_dict.update({})
    #     for view_currency in view_currencies_list:
    #         count_currencies += 1
    #         try:
    #             x = ExchangeRate.objects.filter(date__date=str(
    #                                             view_date),
    #                                             name__name=str(
    #                                             view_currency
    #                                             )).values()  # A
    #             view_exchange_rate_to_chf = x[0]['exchange_rate_to_chf']
    #         except Exception as e:
    #             print('prepare_view %s (%s) for %s on %s is %s'
    #                   % (e, type(e), view_currency, view_date,
    #                      view_exchange_rate_to_chf))
    #             view_exchange_rate_to_chf = " "
    #
    #         view_currency_dict.update({view_currency:
    #                                    view_exchange_rate_to_chf})  # B
    #
    #     view_currency_list.append(view_currency_dict)
    # assert False
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list,
                   'currency_USD_list': currency_USD_list,
                   'currency_EUR_list': currency_EUR_list,
                   'currency_JPY_list': currency_JPY_list,
                   'currency_GBP_list': currency_GBP_list,
                   'count_raw_data': count_raw_data,
                   'message': message})
