from django import forms
from currencies.models import ExchangeRate_name


class CurrencyForm(forms.Form):
    # https://bradmontgomery.net/blog/2008/11/24/a-simple-django-example-with-ajax/
    currencies = forms.ModelChoiceField(
        queryset=ExchangeRate_name.objects.all())

    CURRENCY_CHOICES = [(t.name, t.name) for t in
                        ExchangeRate_name.objects.all()]

    type = forms.ChoiceField(choices=CURRENCY_CHOICES,
                             widget=forms.Select(attrs={
                                'onchange': 'get_vehicle_color();'}))
