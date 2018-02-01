from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from currencies.models import ExchangeRate

class Option(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, unique=True)
    value = models.IntegerField(default=5)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ArticleStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

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


class Order(models.Model):
    """ purchase  """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ManyToManyField(Article, through='OrderPosition')
    status = models.ForeignKey(OrderStatus)
    date = models.DateTimeField(default=timezone.now)


class OrderOfGoods(models.Model):
    """  articles of purchase """
    article = models.ForeignKey(Article)
    amount = models.FloatField(max_length=3)
    delivery_date = models.DateField()
    order = models.ForeignKey(Order)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.ForeignKey(OrderStatus)
    exchange_rate = models.ForeignKey(ExchangeRate)

    class Meta:
        verbose_name_plural = "Order of Goods"


class Picture(models.Model):
    name = models.CharField(max_length=200)
    article = models.ForeignKey(Article)
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    """ cart of user """
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CartOfGoods(models.Model):
    """ cart items """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    amount = models.FloatField(max_length=5)
    cart = models.ForeignKey(ShoppingCart)


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
