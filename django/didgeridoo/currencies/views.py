from django.shortcuts import render
from currencies.models import ExchangeRate
from currencies import exchange_rates


def currencies(request):
    # return HttpResponse("exchange_rates")
    raw_data, date = exchange_rates.get_exchange_rate()
    message = ""
    for currency, rate in raw_data.items():
        if ExchangeRate.objects.filter(date=date):
            message = "already querried today"
        else:
            e = ExchangeRate.objects.create(
                name=currency,
                exchange_rate_to_chf=rate,
                date=date
                )
            e.save()
            message = "updated successfully"
    currency_list = ExchangeRate.objects.all()
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list,
                   'date': date,
                   'message': message})
