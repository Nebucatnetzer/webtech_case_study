from django.shortcuts import render
import datetime
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from currencies.models import (ExchangeRate,
                               ExchangeRate_date,
                               ExchangeRate_name)
from currencies import exchange_rates
from currencies.forms import CurrencyForm
from django.http import JsonResponse


def currency_update(request):
    # https://simpleisbetterthancomplex.com/tutorial/2016/08/29/how-to-work-with-ajax-request-with-django.html
    currency = request.POST.get('currency_update', None)
    data = ExchangeRate.objects.values('exchange_rate_to_chf').latest()
    print('currency: ', currency, 'data: ', data)
    return JsonResponse(data)


def currencies(request):
    # this function fetches the data from exchange_rates.py
    # evaluates if the values are already stored and
    # prepares the view all dynamicaly.
    # It can grow in terms of more Currencies over time automaticaly.
    today = ''
    raw_data = []
    try:
        raw_data, today = exchange_rates.get_exchange_rate()
    except Exception as e:
        print('views raw_data: ', raw_data, 'error:', e)  # assert False
    message_no = "Already querried today: "
    message_yes = " Updated successfully: "
    # raw_data can be empty. In this case skip:
    if raw_data:
        # if raw_data is not empty iterate over items in it:
        for currency, rate in raw_data.items():
            # check for already existing exrates per day and add
            # to message that its already been saved.
            if ExchangeRate.objects.filter(
                    date__date=today,
                    name__name=currency):
                message_no += currency + ", "
            else:
                if ExchangeRate_date.objects.filter(date=today)[:1]:
                    # if data and currency is not yet present, save it.
                    try:
                        # A: https://stackoverflow.com/a/27802801/4061870
                        # lustigerweise gibt .values() den value und die id
                        # zurück. Ohne .values() gibts nur den "value"
                        date_dict = ExchangeRate_date.objects.filter(
                            date=today).values()
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
                    # if data and currency is not yet present, save it.
                    try:
                        name_dict = ExchangeRate_name.objects.filter(
                            name=currency).values()
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
                    # save item to where id's match.
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
    # python can not swap a char insinde a sting so i have
    # to invert and swap and then invert back:
    message_no = message_no[::-1]  # invert the string
    message_no = message_no.replace(",", "!", 1)  # replace first , with !
    message_no = message_no[::-1]  # invert the string back
    message_yes = message_yes[::-1]  # invert the string
    message_yes = message_yes.replace(",", "!", 1)  # replace f. , with !
    message_yes = message_yes[::-1]  # invert the string back
    # here we evaluate what kind of message is valid:
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
    # know we can query our data for presentaton:
    currency_list = ExchangeRate.objects.all()
    currency_USD_list = ExchangeRate.objects.filter(
        name__name='USD').order_by('date__date')
    currency_EUR_list = ExchangeRate.objects.filter(
        name__name='EUR').order_by('date__date')
    currency_JPY_list = ExchangeRate.objects.filter(
        name__name='JPY').order_by('date__date')
    currency_GBP_list = ExchangeRate.objects.filter(
        name__name='GBP').order_by('date__date')
    # and publish it on template:
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list,
                   'currency_USD_list': currency_USD_list,
                   'currency_EUR_list': currency_EUR_list,
                   'currency_JPY_list': currency_JPY_list,
                   'currency_GBP_list': currency_GBP_list,
                   'message': message})
