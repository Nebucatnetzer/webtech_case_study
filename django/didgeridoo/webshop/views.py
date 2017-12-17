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


def articles_in_category(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    hidden = ArticleStatus.objects.get(name="hidden")

    article_list = Article.objects.filter(
        category=selected_category.id).exclude(status=hidden.id)

    template = loader.get_template('webshop/category.html')
    context = {
        'article_list': article_list,
        'category': selected_category,
    }
    return HttpResponse(template.render(context, request))
