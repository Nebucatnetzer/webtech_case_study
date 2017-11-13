from django.contrib import admin

# Register your models here.
from .models import Article
from .models import Order
from .models import Person
from .models import City
from .models import Picture
from .models import OrderOfGoods
from .models import Category
from .models import Option
from .models import Settings

admin.site.register(Article)
admin.site.register(Order)
admin.site.register(Person)
admin.site.register(City)
admin.site.register(Picture)
admin.site.register(OrderOfGoods)
admin.site.register(Category)
admin.site.register(Option)
admin.site.register(Settings)
