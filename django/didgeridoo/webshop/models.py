from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
import datetime


class Option(models.Model):
    name = models.CharField(max_length=200, unique=True)
    value = models.IntegerField(default=5)

    def __str__(self):
        return self.name


class Setting(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.option)


class ArticleStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ExchangeRate(models.Model):
    name = models.CharField(max_length=200, unique=True)
    exchange_rate_to_chf = models.FloatField(max_length=5)

    def __str__(self):
        return self.name


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    parent_category = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Article(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True)
    description = models.TextField(max_length=2000)
    stock = models.FloatField(max_length=5)
    status = models.ForeignKey(ArticleStatus)
    price_in_chf = models.DecimalField(max_digits=19,
                                       decimal_places=2,
                                       validators=[MinValueValidator(
                                           Decimal('0.00'))])

    def __str__(self):
        return self.name


class OrderStatus(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class OrderOfGoods(models.Model):
    article = models.ForeignKey(Article)
    amount = models.FloatField(max_length=5)
    delivery_date = models.DateField()
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.ForeignKey(OrderStatus)

    class Meta:
        verbose_name_plural = "Order of Goods"


class Picture(models.Model):
    name = models.CharField(max_length=200, unique=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ManyToManyField(Article, through='OrderPosition')
    status = models.ForeignKey(OrderStatus)
    date = models.DateTimeField(default=datetime.datetime.now())


class OrderPosition(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=5)
    price_in_chf = models.DecimalField(max_digits=19,
                                       decimal_places=2,
                                       validators=[MinValueValidator(
                                            Decimal('0.00'))])


class ShoppingCart(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ManyToManyField(Article)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=200)
    zip_code = models.PositiveSmallIntegerField()

    def __str__(self):
        return '{} {}'.format(self.zip_code, self.name)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['zip_code']


class Salutation(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Person(models.Model):
    salutation = models.ForeignKey(Salutation)
    city = models.ForeignKey(City)
    street_name = models.CharField(max_length=200)
    street_number = models.CharField(max_length=4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
