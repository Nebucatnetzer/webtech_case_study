from django import forms
from currencies.models import ExchangeRate_name


class CurrencyForm(forms.Form):
        currencies = forms.ModelChoiceField(
            queryset=ExchangeRate_name.objects.all())
