from django.conf.urls import url
from currencies.views import currencies, currency_update


urlpatterns = [
    url(r'^currencies/$', currencies),
    url(r'^ajax/currency_update/$',
        currency_update,
        name='currency_update'),
]
