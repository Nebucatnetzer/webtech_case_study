from django.shortcuts import render
from .models import ExchangeRate
import exchange_rates


def currencies(request):
    # return HttpResponse("exchange_rates")
    currency_list = ExchangeRate.objects.all()
    raw_data = exchange_rates.get_exchange_rate()

    for i, j in raw_data.items:
        ExchangeRate.objects.create(
            name=i,
            exchange_rate_to_chf=j)

    return render(request,
                  'currencies/index.html',
                  {'currency_list': currency_list})
