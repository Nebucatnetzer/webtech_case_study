from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

from .models import Article, Category, ArticleStatus

# Create your views here.


def index(request):
    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}

    for i in parent_category_list:
            category = Category.objects.filter(parent_category=i.id)
            category_list[i] = category

    template = loader.get_template('webshop/index.html')
    context = {
        'category_list': category_list,
        'parent_category_list': parent_category_list,
    }
    return HttpResponse(template.render(context, request))
