from django.db import models


class ExchangeRate(models.Model):
    name = models.CharField(max_length=200, unique=True)
    exchange_rate_to_chf = models.FloatField(max_length=5)

    def __str__(self):
        return self.name
