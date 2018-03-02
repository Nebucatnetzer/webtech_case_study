from django.db import models


class ExchangeRate_name(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class ExchangeRate_date(models.Model):
    date = models.DateField('%Y-%m-%d', unique_for_date=True)

    def __str__(self):
        return str(self.date)


class ExchangeRate(models.Model):
    name = models.ForeignKey(ExchangeRate_name)
    date = models.ForeignKey(ExchangeRate_date)
    exchange_rate_to_chf = models.DecimalField(max_digits=12,
                                               decimal_places=5)

    def exchange(_currency_id, _base_currency):
        rate = ExchangeRate.objects.filter(name=_currency_id).latest('date')
        return round(rate.exchange_rate_to_chf * _base_currency,2)

    def __str__(self):
        return str(self.name)
