from django.shortcuts import render
from datetime import datetime
from currencies.models import (ExchangeRate,
                               ExchangeRate_date,
                               ExchangeRate_name)
from currencies import exchange_rates
from django.http import JsonResponse


def currencies(request):

    """this function fetches the data from swiss national bank
    evaluates if the values are already stored and
    prepares a view all dynamicaly.
    It can grow in terms of more Currencies over time automaticaly."""

    message_offline = ''

    # Namespaces
    ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
          'none': 'http://purl.org/rss/1.0/',
          'dc': 'http://purl.org/dc/elements/1.1/',
          'dcterms': 'http://purl.org/dc/terms/',
          'cb': 'http://www.cbwiki.net/wiki/index.php/Specification_1.2/'
          }
    SNB_URL = 'https://www.snb.ch/selector/de/mmr/exfeed/rss'
    try:
        urlsocket = exchange_rates.get_rss(SNB_URL)
    except Exception as e:
        print('currencies/views.currencies() get_rss() error:', e)
    try:
        rss_tree = exchange_rates.parse_rss(urlsocket)
    except Exception as e:
        print('currencies/views.currencies() parse_rss() error:', e)
    try:
        raw_data = exchange_rates.get_exchange_rate(rss_tree, ns)
    except Exception as e:
        print('currencies/views.currencies() get_exchange_rate() error:', e)
        # because url seams to be not avalable we fetch a local file in root
        # didgeridoo/rss to get some older currencies.
        rss_tree = exchange_rates.pass_local_file()
        message_offline = """
        Are you offline? - useing stored currencies.
        This does not efect you, but your purchase prices will be
        recalculated as soon as you submit your Order.
        """
        try:
            raw_data = exchange_rates.get_exchange_rate(rss_tree, ns)
        except Exception as e:
            print("""currencies/views.currencies()
                get_exchange_rate.pass_local_file() error:""", e)
    today = datetime.now().strftime("%Y-%m-%d")

    message_no = "Already querried: "
    length_of_message_no = len(message_no)
    message_yes = " Updated successfully: "
    length_of_message_yes = len(message_yes)
    # raw_data can be empty. In this case skip:
    if raw_data:
        for one_obj_of_list in raw_data:
            for exchange_rate_of_one_day in one_obj_of_list:
                date = exchange_rate_of_one_day['date']
                currency = exchange_rate_of_one_day['currency']
                exchangerate = exchange_rate_of_one_day['exchangerate']
                # check for already existing exrates per day and add
                # to message that its already been saved.
                if ExchangeRate.objects.filter(
                        date__date=date,
                        name__name=currency):
                    message_no += currency + ' on ' + date + ", "
                else:
                    if ExchangeRate_date.objects.filter(date=date)[:1]:
                        # if data and currency is not yet present, save it.
                        try:
                            # A: https://stackoverflow.com/a/27802801/4061870
                            # lustigerweise gibt .values() den value und die id
                            # zurück. Ohne .values() gibts nur den "value"
                            date_dict = ExchangeRate_date.objects.filter(
                                date=date).values()
                        except Exception as e:
                            print('currencies/views/exdate_exists \
                                %s (%s) on %s'
                                  % (e, type(e), today))
                    else:
                        try:
                            exdate = ExchangeRate_date.objects.create(
                                date=date)
                            exdate.save()
                        except Exception as e:
                            print('currencies/views/exdate_not_exists \
                                %s (%s) for %s'
                                  % (e, type(e), date))
                    if ExchangeRate_name.objects.filter(
                            name=currency)[:1]:
                        # if data and currency is not yet present, save it.
                        try:
                            name_dict = ExchangeRate_name.objects.filter(
                                name=currency).values()
                        except Exception as e:
                            print('currencies/views/exname_exists \
                                %s (%s) on %s'
                                  % (e, type(e), currency))
                    else:
                        try:
                            exname = ExchangeRate_name.objects.create(
                                name=currency)
                            exname.save()
                        except Exception as e:
                            print('currencies/views/exname_not_exists \
                                %s (%s) on %s'
                                  % (e, type(e), currency))
                    try:
                        # save item to where id's match.
                        exrate = ExchangeRate.objects.create(
                            # name_id=name_id,
                            name_id=ExchangeRate_name.objects.get(
                                name=currency).id,
                            # date_id=date_id,
                            date_id=ExchangeRate_date.objects.get(
                                date=date).id,
                            exchange_rate_to_chf=exchangerate,
                            )
                        exrate.save()
                        message_yes += currency + ' on ' + date + ", "

                    except Exception as e:
                        print('currencies/views/exrate_create \
                            %s (%s) on %s for %s'
                              % (e, type(e), currency, date))

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
    if len(message_no) > length_of_message_no\
            and len(message_yes) > length_of_message_yes:
        message = message_offline + message_no + message_yes
    elif len(message_no) > 24:
        message = message_offline + message_no
    elif len(message_yes) > 18:
        message = message_offline + message_yes
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
