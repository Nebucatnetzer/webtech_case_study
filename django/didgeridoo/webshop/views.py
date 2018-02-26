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
                            ShoppingCart,
                            Order,
                            OrderStatus)
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


def restrict_cart_to_one_article(user_id, article_id, amount, operation):
    # if cart_id is not existent create a cart:
    cart_id, created_cart = ShoppingCart.objects.get_or_create(user=user_id)
    article = Article.objects.get(id=article_id)
    # transfair Article to CartPosition:
    cart_position, created_position = CartPosition.objects.get_or_create(
        article=article,
        defaults={'amount': amount,
                  'position_price': article.price_in_chf,
                  'cart': cart_id
                  }
        )
    if created_position is False:
        if operation == 'delete':
            cart_position.delete()
        if (operation == 'add') or (operation == 'replace'):
            if operation == 'add':
                new_amount = cart_position.amount + amount
            if operation == 'replace':
                new_amount = amount
            # if article is in cart already update amount:
            cart_position = CartPosition.objects.filter(
                article=article_id).update(
                amount=new_amount
                )


def article_details(request, article_id):
    category_list = get_categories()
    currencies_form = CurrenciesForm
    amount = AddToCartForm
    rate = ExchangeRate
    article_view = True
    currency_name = "CHF"
    user = request.user

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
                operation = 'add'
                restrict_cart_to_one_article(
                    user,
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


@login_required
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
    cart_position_list_zip = []

# here we configure the users Currency:
    if 'currency' not in request.session:
        request.session['currency'] = None
    else:
        currency = request.session['currency']

# Here we handle all POST Operations:
    if request.method == 'POST':
        # here we react to a currency dropdown change:
        if 'currencies' in request.POST:
            print('currencies')
            currencies_form = CurrenciesForm(request.POST)
            if currencies_form.is_valid():
                cf = currencies_form.cleaned_data
                if cf['currencies']:
                    print('currencies cf:', cf)
                    selection = cf['currencies']
                    request.session['currency'] = selection.id
                    currency_name = ExchangeRate_name.objects.get(
                        id=selection.id)
                    print('currencies currency_name:', currency_name)
                else:
                    request.session['currency'] = None

        # here we react to a change of amount per item in the Cart:
        if 'amount_form' in request.POST:
            amount_form = CartForm(request.POST)
            if amount_form.is_valid():
                amount = amount_form.cleaned_data['amount_form']
                article_id = request.POST.get('article_id')
                operation = 'replace'
                restrict_cart_to_one_article(
                    request.user.id,
                    article_id,
                    amount,
                    operation
                    )

        # here we react to a change of amount per item in the Cart:
        if 'delete' in request.POST:
            delete = CartForm(request.POST)
            if delete.is_valid():
                amount = delete.cleaned_data['amount_form']
                article_id = request.POST.get('article_id')
                amount = 1
                operation = 'delete'
                restrict_cart_to_one_article(
                    request.user.id,
                    article_id,
                    amount,
                    operation
                    )

    # here we handle the normal cart view:
    # if cart_id is not existent create a cart:
    cart_id, created_cart = ShoppingCart.objects.get_or_create(
        user=request.user
    )
    # get all items in the cart of this customer:
    cart_positions = CartPosition.objects.filter(cart=cart_id)
    if (cart_positions.count()) > 0:
        # make a list out of all articles:
        cart_position_list = list(cart_positions)
        # enumerate the list of articles and loop over items:
        for idx, cart_position in enumerate(cart_position_list):
            # scrap out the details to calculate Total of item and Summ of All:
            if request.session['currency']:
                currency = request.session['currency']
                # get currencyname to display:
                currency_name = ExchangeRate_name.objects.get(id=currency)
                # get exchange_rate multiplyed:
                cart_position.article.price_in_chf = rate.exchange(
                    currency,
                    cart_position.article.price_in_chf
                    )
            amount_form = CartForm(
                initial={'amount_form': cart_position.amount}
            )
            cart_position.calculate_position_price()
            totalprice_list.append(cart_position.position_price)
            amount_form_list.append(amount_form)
            cart_position_list[idx] = cart_position
        cart_position_list_zip = zip(cart_position_list, amount_form_list)

    total = sum(totalprice_list)

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


@login_required
def checkout(request):
    category_list = get_categories()
    rate = ExchangeRate
    article_view = False
    message = ""
    cart_position_list = []
    totalprice_list = []
    total = 0

    checkout_form = CheckoutForm()
    if 'currency' not in request.session:
        request.session['currency'] = None
    else:
        currency = request.session['currency']
    exchange_rate = ExchangeRate.objects.filter(name=currency).latest('date')
    # Here we handle all POST Operations:
    if request.method == 'POST':
        print('checkout post', request.POST)
        # here we react to a change of amount per item in the Cart:
        if 'checkout' in request.POST:
            print('checkout post request.POST = checkout_form')
            checkout_form = CheckoutForm(request.POST)
            if checkout_form.is_valid():
                orderstatus = OrderStatus.objects.get(name='ordered')
                print('checkout post valid orderstatus', orderstatus,
                      'exchange_rate_id:', exchange_rate_id)
                order, created_order = Order.objects.get_or_create(
                    user=request.user,
                    defaults={'status': orderstatus,
                              'exchange_rate': exchange_rate,
                              }
                    )
                print('order', order, 'created:', created_order)
                if created_order is False:
                    message = """something whent wrong.
                    Seams like this cart was already submitted. How come? """
                    #  order status variables:
                    #  • ordered -> vom Kunden bestellt
                    #  • delivered -> Bestellung wurde versandt
                    #  • cancelled -> Bestellung storniert
                    #  • on hold -> Bestellung pausiert

    cart_id, created_cart = ShoppingCart.objects.get_or_create(
        user=request.user)
    if created_cart is False:
        # get all items in the cart of this customer:
        cart_positions = CartPosition.objects.filter(
            cart=cart_id)
        if (cart_positions.count()) > 0:
            # make a list out of all articles:
            cart_position_list = list(cart_positions)
            # enumerate the list of articles and loop over items:
            for idx, cart_position in enumerate(cart_position_list):
                if currency:
                    # get currencyname to display:
                    currency_name = ExchangeRate_name.objects.get(id=currency)
                    # get exchange_rate multiplyed:
                    cart_position.article.price_in_chf = rate.exchange(
                        currency,
                        cart_position.article.price_in_chf
                        )
                cart_position.calculate_position_price()
                totalprice_list.append(cart_position.position_price)
                cart_position_list[idx] = cart_position
    else:
        message = """something whent wrong.
                     Seams like your cart was
                     not existent before. How come? """
    total = sum(totalprice_list)
    person = Person.objects.get(user=request.user.id)

    return render(request, 'webshop/checkout.html',
                  {'cart_position_list': cart_position_list,
                   'total': total,
                   'checkout_form': checkout_form,
                   'currency_name': currency_name,
                   'article_view': article_view,
                   'category_list': category_list,
                   'message': message,
                   'person': person
                   })


def order(request):
    return render(request, 'webshop/order.html',
                  {

                  })
