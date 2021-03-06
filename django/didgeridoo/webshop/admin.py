from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from webshop.models import (Article, Order, OrderPosition,
                            Person, City, Picture, OrderOfGoods,
                            Category, Option)

from webshop.forms import PictureForm


class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'person'


class PictureAdmin(admin.ModelAdmin):
    form = PictureForm
    ordering = ('name',)
    list_display = ('name', 'article',)


class PictureInline(admin.StackedInline):
    model = Picture
    form = PictureForm
    can_delete = False
    verbose_name_plural = 'pictures'


class OptionAdmin(admin.ModelAdmin):
    model = Option
    list_display = ('name', 'description',)
    readonly_fields = ('name', 'description',)

    def get_actions(self, request):
        # Disable delete
        actions = super(OptionAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def has_add_permission(self, request):
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


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

admin.site.register(Article)
admin.site.register(Order, OrderAdmin)
admin.site.register(Picture, PictureAdmin)
admin.site.register(City)
admin.site.register(OrderOfGoods, OrderOfGoodsAdmin)
admin.site.register(Category)
admin.site.register(Option, OptionAdmin)
