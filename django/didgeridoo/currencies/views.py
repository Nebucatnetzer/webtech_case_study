from django.shortcuts import render
from currencies.models import ExchangeRate
from currencies import exchange_rates


def currencies(request):
    # return HttpResponse("exchange_rates")
    raw_data = exchange_rates.get_exchange_rate()
    for i, j in raw_data.items():
        if ExchangeRate.objects.filter(name=i):
            e = ExchangeRate.objects.filter(
                name=i,
                ).update(
                exchange_rate_to_chf=j
                )
        else:
            e = ExchangeRate.objects.create(
                name=i,
                exchange_rate_to_chf=j
                )
            e.save()
    currency_list = ExchangeRate.objects.all()
    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list})
