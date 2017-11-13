from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    article_id = models.ForeignKey('self')


class Option(models.Model):
    name = models.CharField(max_length=200, unique=True)
    value = models.IntegerField(default=5)


class Settings(models.Model):
    option_id = models.ForeignKey(Option, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)


class DeliveryStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)


class ArticleStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)


class ExchangeRate(models.Model):
    name = models.CharField(max_length=200, unique=True)
    exchange_rate_to_chf = models.FloatField(max_length=5)


class Article(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    stock = models.FloatField(max_length=5)
    status_id = models.ForeignKey(ArticleStatus, on_delete=models.CASCADE)
    price_in_chf = models.DecimalField(max_digits=19, decimal_places=2)


class OrderOfGoods(models.Model):
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=5)
    delivery_date = models.DateField()
    order_date = models.DateTimeField(auto_now_add=True)


class Picture(models.Model):
    name = models.CharField(max_length=200, unique=True)
    article_id = models.ForeignKey(Article, on_delete=models.CASCADE)


class OrderStatus(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.ManyToManyField(Article)
    order_status_id = models.ForeignKey(OrderStatus)


class ShoppingCart(models.Model):
    name = models.CharField(max_length=200)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.ManyToManyField(Article)


class City(models.Model):
   name = models.CharField(max_length=200)
   plz = models.PositiveSmallIntegerField()


class Salution(models.Model):
    name = models.CharField(max_length=20)


class Person(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    salution_id= models.ForeignKey(Salution)
    city_id= models.ForeignKey(City)
    street_name = models.CharField(max_length=200)
    street_number = models.CharField(max_length=4)
