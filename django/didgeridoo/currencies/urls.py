from django.conf.urls import url
from currencies.views import currencies, CurrencyUpdate


urlpatterns = [
    url(r'^currencies/$', currencies),
    url(r'^ajax/CurrencyUpdate/$',
        CurrencyUpdate,
        name='CurrencyUpdate'),
]
