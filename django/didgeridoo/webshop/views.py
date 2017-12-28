from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from webshop.models import Article, Category, ArticleStatus, Person

# Create your views here.


def index(request):
    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}

    for i in parent_category_list:
            category_list.update(
                {i: Category.objects.filter(parent_category=i.id)})

    return render(request,
                  'webshop/index.html',
                  {'category_list': category_list})


def articles_in_category(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    hidden = ArticleStatus.objects.get(name="hidden")

    article_list = Article.objects.filter(
        category=selected_category.id).exclude(status=hidden.id)

    return render(request, 'webshop/category.html',
                  {'article_list': article_list,
                   'category': selected_category})


def article_details(request, article_id):
        article = get_object_or_404(Article, pk=article_id)
        return render(request, 'webshop/article_details.html',
                      {'article': article})


@login_required
def profile(request):
    person = Person.objects.get(user=request.user)
    return render(request, 'registration/profile.html',
                  {'person': person})
