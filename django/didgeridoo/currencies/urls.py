from django.conf.urls import url
from currencies.views import currencies

urlpatterns = [
    url(r'^currencies/$', currencies),
]
