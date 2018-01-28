from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from webshop.models import (Article, Category, ArticleStatus, Person,
                            City, Picture)
from webshop.forms import RegistrationForm

from currencies.models import ExchangeRate, ExchangeRate_name
from currencies.forms import CurrenciesForm


# Create your views here.

def get_categories():
    parent_category_list = Category.objects.filter(parent_category=None)
    category_list = {}

    for i in parent_category_list:
            category_list.update(
                {i: Category.objects.filter(parent_category=i.id)})
    return category_list


def get_hidden_status_id():
    hidden_status = ArticleStatus.objects.get(name="hidden")
    return hidden_status.id


def index(request):
    category_list = get_categories()
    articles = Article.objects.all().exclude(status=get_hidden_status_id())
    articles_list = list(articles)
    currencies_form = CurrenciesForm
    rate=ExchangeRate
    article_view = True
    currency_name = "CHF"

    if request.method == 'POST':
        currencies_form = CurrenciesForm(request.POST)
        if currencies_form.is_valid():
            cf = currencies_form.cleaned_data
            if cf['currencies']:
                selection = cf['currencies']
                request.session['currency'] = selection.id
                currency_name=ExchangeRate_name.objects.get(id=selection.id)
            else:
                request.session['currency'] = None

    if request.session['currency']:
        currency = request.session['currency']
        for idx, article in enumerate(articles_list):
            article.price_in_chf = rate.exchange(currency, article.price_in_chf)
            articles_list[idx] = article
            currency_name=ExchangeRate_name.objects.get(id=currency)

    return render(request,
                'webshop/index.html',
                {'category_list': category_list,
                 'articles_list': articles_list,
                 'currencies_form': currencies_form,
                 'article_view': article_view,
                 'currency_name': currency_name})


def articles_in_category(request, category_id):
    category_list = get_categories()
    selected_category = Category.objects.get(id=category_id)
    hidden = ArticleStatus.objects.get(name="hidden")

    articles_list = Article.objects.filter(
        category=selected_category.id).exclude(status=get_hidden_status_id())


    return render(request, 'webshop/category.html',
                  {'articles_list': articles_list,
                   'category_list': category_list,
                   'category': selected_category})


def article_details(request, article_id):
    category_list = get_categories()

    article = get_object_or_404(Article, pk=article_id)
    picture_list = Picture.objects.filter(article=article_id)
    return render(request, 'webshop/article_details.html',
                  {'article': article,
                   'category_list': category_list,
                   'picture_list': picture_list})

@login_required
def profile(request):
    category_list = get_categories()
    person = Person.objects.get(user=request.user)
    return render(request, 'registration/profile.html',
                  {'person': person,
                   'category_list': category_list})


def registration(request):
    category_list = get_categories()
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
                   'category_list': category_list,
                   'user_form': user_form})
