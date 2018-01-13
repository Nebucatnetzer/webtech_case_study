from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from webshop.models import (Article, Order, OrderPosition,
                            Person, City, Picture, OrderOfGoods,
                            Category, Option, Setting)


class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'person'


class PictureInline(admin.StackedInline):
    model = Picture
    can_delete = False
    verbose_name_plural = 'pictures'


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


class ArticleAdmin(admin.ModelAdmin):
    inlines = (PictureInline,)


class OrderPositionInline(admin.StackedInline):
    model = OrderPosition
    can_delete = False
    verbose_name_plural = 'Order Positions'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date')
    list_filter = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    inlines = (OrderPositionInline,)


class OrderOfGoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'order_status', 'order_date')
    list_filter = ('order_date',)
    date_hierarchy = 'order_date'
    ordering = ('-order_date',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(City)
admin.site.register(OrderOfGoods, OrderOfGoodsAdmin)
admin.site.register(Category)
admin.site.register(Option)
admin.site.register(Setting)
