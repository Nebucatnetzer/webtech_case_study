from django import forms
from currencies.models import ExchangeRate_name


class CurrenciesForm(forms.Form):
    currencies = forms.ModelChoiceField(
        queryset=ExchangeRate_name.objects.all(),
                required=False, empty_label='CHF')
