from django.db import models
import exchange_rates


class ExchangeRate(models.Model):
    name = models.CharField(max_length=200, unique=True)
    exchange_rate_to_chf = models.FloatField(max_length=5)

    def __str__(self):
        return self.name

    def exchange_rates():
        exchange_rates = currencies.get_exchange_rate()

        for i in exchange_rates:
            if ExchangeRate.objects.filter(
                    name='exchange_rates_data[dictionary_value]'):
                ExchangeRate.objects.filter(
                    name='exchange_rates_data[dictionary_key]',
                    exchange_rate_to_chf=exchange_rates.value).save()
