from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from webshop.models import (Article,
                            Category,
                            Person,
                            City,
                            Picture,
                            CartPosition,
                            ShoppingCart)
from webshop.forms import (RegistrationForm,
                           AddToCartForm,
                           CartForm,
                           CheckoutForm)
from webshop.utils import (get_categories,
                           get_hidden_status_id,
                           process_article_prices)

from currencies.models import ExchangeRate, ExchangeRate_name
from currencies.forms import CurrenciesForm


def index(request):
    category_list = get_categories()
    currencies_form = CurrenciesForm
    article_view = True

    articles = Article.objects.all().exclude(status=get_hidden_status_id())
    return_values = process_article_prices(request, articles)
    articles_list = return_values['articles_list']
    currency_name = return_values['currency_name']

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

    currencies_form = CurrenciesForm
    article_view = True

    articles = Article.objects.filter(
        category=selected_category.id).exclude(status=get_hidden_status_id())
    return_values = process_article_prices(request, articles)
    articles_list = return_values['articles_list']
    currency_name = return_values['currency_name']

    return render(request, 'webshop/category.html',
                  {'articles_list': articles_list,
                   'category_list': category_list,
                   'currencies_form': currencies_form,
                   'article_view': article_view,
                   'currency_name': currency_name,
                   'category': selected_category})


def restrict_cart_to_one_article(user_name, article_id, amount, operation):
    article = Article.objects.get(id=article_id)
    try:
        # lookup if cart_id is already existent:
        cart_id = ShoppingCart.objects.get(user=user_name)
    except:
        # if cart_id is not existent create a cart:
        cart_id = ShoppingCart.objects.create(user=user_name)
        cart_id.save()
    if cart_id:
        print('restrict_cart_to_one_article cart_id:', cart_id)
        # check if the article is existent in cart already:
        try:
            article_amount = CartPosition.objects.get(
                article=article_id)
            if operation == 'add':
                new_amount = article_amount.amount + amount
                print('restrict_cart_to_one_article add new_amount:', new_amount,
                      'article_id', article_id)
            if operation == 'replace':
                new_amount = amount
                print('restrict_cart_to_one_article replace:', new_amount,
                      'article_id', article_id)
            # if article is in cart already update amount:
            cart_position = CartPosition.objects.filter(
                id=article_id).update(
                amount=new_amount
                )
        except Exception as e:
            print('restrict_cart_to_one_article except: ', e)
            # if the article is not in cart yet add full item:
            cart_position = CartPosition.objects.create(
                article=article,
                amount=amount,
                position_price=article.price_in_chf,
                cart=ShoppingCart.objects.get(user=user_name)
                )
            cart_position.save()


def article_details(request, article_id):
    category_list = get_categories()
    currencies_form = CurrenciesForm
    amount = AddToCartForm
    rate = ExchangeRate
    article_view = True
    currency_name = "CHF"

    if 'currency' not in request.session:
        request.session['currency'] = None

    article = get_object_or_404(Article, pk=article_id)
    picture_list = Picture.objects.filter(article=article_id)

    if request.method == 'POST':
        # hier wird das Currency dropdown bearbeitet:
        if 'currencies' in request.POST:
            currencies_form = CurrenciesForm(request.POST)
            if currencies_form.is_valid():
                cf = currencies_form.cleaned_data
                if cf['currencies']:
                    selection = cf['currencies']
                    request.session['currency'] = selection.id
                    currency_name = ExchangeRate_name.objects.get(
                        id=selection.id)
                else:
                    request.session['currency'] = None

        # hier wird der Artikel in den Wahrenkorb transferiert:
        if 'amount' in request.POST:
            amount = AddToCartForm(request.POST)
            if amount.is_valid():
                amount = amount.cleaned_data['amount']
                user_name = request.user
                operation = 'add'
                restrict_cart_to_one_article(
                    user_name,
                    article_id,
                    amount,
                    operation
                    )
                # write default value (1) to form field:
                amount = AddToCartForm()
        else:
            amount = AddToCartForm()

    if request.session['currency']:
        currency = request.session['currency']
        article.price_in_chf = rate.exchange(currency, article.price_in_chf)
        currency_name = ExchangeRate_name.objects.get(id=currency)

    return render(request, 'webshop/article_details.html',
                  {'article': article,
                   'category_list': category_list,
                   'currencies_form': currencies_form,
                   'article_view': article_view,
                   'currency_name': currency_name,
                   'picture_list': picture_list,
                   'amount': amount
                   })


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
                with transaction.atomic():
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


def cart(request):
    category_list = get_categories()
    currencies_form = CurrenciesForm
    amount_form = CartForm
    rate = ExchangeRate
    article_view = True
    currency_name = "CHF"
    message = ""
    cart_position_list = []
    amount_form_list = []
    totalprice_list = []
    total = 0
    user_name = request.user
    cart_position_list_zip = []

# here we configure the users Currency:
    if 'currency' not in request.session:
        request.session['currency'] = None
    else:
        currency = request.session['currency']

# Here we handle all POST Operations:
    if request.method == 'POST':
        print(request.POST)
        # here we react to a currency dropdown change:
        if 'currencies' in request.POST:
            print('currencies')
            currencies_form = CurrenciesForm(request.POST)
            if currencies_form.is_valid():
                cf = currencies_form.cleaned_data
                if cf['currencies']:
                    selection = cf['currencies']
                    request.session['currency'] = selection.id
                    currency_name = ExchangeRate_name.objects.get(
                        id=selection.id)
                else:
                    request.session['currency'] = None
        # here we react to a change of amount per item in the Cart:
        if 'amount_form' in request.POST:
            print('amount_form yes amount post')
            amount_form = CartForm(request.POST)
            if amount_form.is_valid():
                amount = amount_form.cleaned_data['amount_form']
                article_id = request.POST.get('article_id')
                operation = 'replace'
                restrict_cart_to_one_article(
                    user_name,
                    article_id,
                    amount,
                    operation
                    )

        if 'checkout' in request.POST:
            print('checkout')
            checkout_form = CheckoutForm(request.POST)
            if checkout_form.is_valid():
                checkout_form = checkout_form.cleaned_data['checkout']
                print('views checkout checkout_form', checkout_form)
                if checkout_form is True:
                    # todo add to order
                    order = ''
# here we handle the normal cart view:
    # if the cart_id is set the user has already added items to cart.
    try:
        cart_id = ShoppingCart.objects.get(user=request.user.id)
    except Exception as e:
        message = "You have no items in the Basket"
        print('try cart_id exception as: ', e)
        cart_id = False
    if cart_id:
        print('cart cart_id', cart_id)
        # get all items in the cart of this customer:
        articles = CartPosition.objects.filter(cart=cart_id)
        # make a list out of all articles:
        cart_position_list = list(articles)
        # enumerate the list of articles and loop over items:
        for idx, cart_position in enumerate(cart_position_list):
            # sub funciton of CartPosition:
            cart_position.calculate_position_price()
            # scrap out the details to calculate Total of item and Summ of All:
            if currency:
                print('calc currency')
                # get currencyname to display:
                currency_name = ExchangeRate_name.objects.get(id=currency)
                # get exchange_rate multiplyed:
                cart_position.price_in_chf = rate.exchange(
                    currency,
                    cart_position.article.price_in_chf
                    )
                totalprice_list.append(cart_position.price_in_chf)

            print('cart cart_position.article.id', cart_position.article.id,
                  'articleamount:', cart_position.amount)
            amount_form = CartForm(
                initial={'amount_form': cart_position.amount}
            )
            amount_form_list.append(amount_form)
            cart_position_list[idx] = cart_position
        cart_position_list_zip = zip(cart_position_list, amount_form_list)

    total = sum(totalprice_list)

    checkout_form = CheckoutForm()

    return render(request, 'webshop/cart.html',
                  {'cart_position_list_zip': cart_position_list_zip,
                   'totalprice_list': totalprice_list,
                   'total': total,
                   'currencies_form': currencies_form,
                   'amount_form': amount_form,
                   'article_view': article_view,
                   'currency_name': currency_name,
                   'category_list': category_list,
                   'message': message,
                   })
