from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from webshop.models import (Article,
                            Category,
                            ArticleStatus,
                            Person,
                            City,
                            Picture)
from webshop.forms import RegistrationForm


# Create your views here.


def index(request):
    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}
    hidden = ArticleStatus.objects.get(name="hidden")
    articles_list = Article.objects.all().exclude(status=hidden.id)

    for i in parent_category_list:
            category_list.update(
                {i: Category.objects.filter(parent_category=i.id)})

    return render(request,
                  'webshop/index.html',
                  {'category_list': category_list,
                   'articles_list': articles_list})


def articles_in_category(request, category_id):
    selected_category = Category.objects.get(id=category_id)
    hidden = ArticleStatus.objects.get(name="hidden")

    article_list = Article.objects.filter(
        category=selected_category.id).exclude(status=hidden.id)

    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}

    for i in parent_category_list:
            category_list.update(
                {i: Category.objects.filter(parent_category=i.id)})

    return render(request, 'webshop/category.html',
                  {'article_list': article_list,
                   'category_list': category_list,
                   'category': selected_category})


def article_details(request, article_id):
    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}

    for i in parent_category_list:
            category_list.update(
                {i: Category.objects.filter(parent_category=i.id)})

    article = get_object_or_404(Article, pk=article_id)
    picture_list = Picture.objects.filter(article=article_id)
    return render(request, 'webshop/article_details.html',
                  {'article': article,
                   'category_list': category_list,
                   'picture_list': picture_list})

@login_required
def profile(request):
    person = Person.objects.get(user=request.user)
    return render(request, 'registration/profile.html',
                  {'person': person})


def registration(request):
    if request.method == 'POST':
            profile_form = RegistrationForm(request.POST)
            user_form = UserCreationForm(request.POST)
            if (profile_form.is_valid() and user_form.is_valid()):
                pf = profile_form.cleaned_data
                uf = user_form.cleaned_data
                user = User.objects.create_user(uf['username'],
                                                pf['email'],
                                                uf['password2'])
                user.last_name = pf['last_name']
                user.first_name = pf['first_name']
                user.save()
                person = Person.objects.create(
                    salutation=pf['salutation'],
                    city=City.objects.get(zip_code=pf['zip_code'],
                                          name=pf['city']),
                    street_name=pf['street_name'],
                    street_number=pf['street_number'],
                    user=user)
                return HttpResponseRedirect('/login/')
    else:
        profile_form = RegistrationForm
        user_form = UserCreationForm
    return render(request, 'registration/register.html',
                  {'profile_form': profile_form,
                   'user_form': user_form})
