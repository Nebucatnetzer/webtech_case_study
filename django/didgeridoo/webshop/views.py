from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from decimal import Decimal
from webshop.models import (Article,
                            Category,
                            Person,
                            City,
                            Picture,
                            CartPosition,
                            ShoppingCart,
                            Order,
                            OrderStatus,
                            OrderPosition)
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
    totalprice_list = []
    total_list = []
    currency_list = []
    order_list_zip = []
    order_positions_count_list = []
    order_positions_count = ""
    total = ""
    currency_name = ""
    person = Person.objects.get(user=request.user)
    orders = Order.objects.filter(user=request.user)
    if orders:
        orders_list = list(orders)
        for idx1, order in enumerate(orders_list):
            # get all items in the Order:
            order_positions = OrderPosition.objects.filter(order=order)
            if (order_positions.count()) > 0:
                order_positions_count = order_positions.count()
                order_positions_count_list.append(order_positions_count)
            orders_list[idx1] = order
        order_list_zip = zip(orders_list,
                             order_positions_count_list
                             )
    # assert False
    return render(request, 'registration/profile.html',
                  {'person': person,
                   'order_list_zip': order_list_zip,
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
                    Person.objects.create(
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
    currency_name = "CHF"
    exchange_rate = False
    message = ""
    cart_position_list = []
    totalprice_list = []
    total = 0
    person = Person.objects.get(user=request.user.id)

    checkout_form = CheckoutForm()
    if 'currency' not in request.session:
        request.session['currency'] = None
    else:
        currency = request.session['currency']

    if currency:
        exchange_rate = rate.objects.filter(name=currency).latest('date')

    cart = ShoppingCart.objects.get(user=request.user)
    if cart:
        # get all items in the cart of this customer:
        cart_positions = CartPosition.objects.filter(cart=cart)
        if (cart_positions.count()) > 0:
            # make a list out of all articles:
            cart_position_list = list(cart_positions)
            # enumerate the list of articles and loop over items:
            for idx, cart_position in enumerate(cart_position_list):
                if request.session['currency']:
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

    # Here we handle all POST Operations:
    if request.method == 'POST':
        # here we react to a change of amount per item in the Cart:
        if 'checkout' in request.POST:
            checkout_form = CheckoutForm(request.POST)
            if checkout_form.is_valid():
                orderstatus = OrderStatus.objects.get(name='ordered')
                if exchange_rate:
                    order = Order.objects.create(user=request.user,
                                                 status=orderstatus,
                                                 exchange_rate=exchange_rate)
                else:
                    order = Order.objects.create(user=request.user,
                                                 status=orderstatus)
                for position in cart_positions:
                    article = Article.objects.get(pk=position.article.id)
                    OrderPosition.objects.create(
                        article=position.article,
                        order=order,
                        amount=position.amount,
                        price_in_chf=article.price_in_chf * Decimal.from_float(
                            position.amount)
                        )
                return HttpResponseRedirect('/order/%s/' % order.id)

    return render(request, 'webshop/checkout.html',
                  {'cart_position_list': cart_position_list,
                   'total': total,
                   'checkout_form': checkout_form,
                   'currency_name': currency_name,
                   'article_view': article_view,
                   'category_list': category_list,
                   'message': message,
                   'person': person,
                   'exchange_rate': exchange_rate,
                   })


def order(request, order_id):
    category_list = get_categories()
    price_list = []
    totalprice_list = []
    order_position_list_zip = []
    cart = ShoppingCart.objects.get(user=request.user)
    if cart:
        # get all items in the cart of this customer:
        cart_positions = CartPosition.objects.filter(cart=cart)
        if (cart_positions.count()) > 0:
            for cart_position in cart_positions:
                restrict_cart_to_one_article(
                    request.user,
                    cart_position.article.id,
                    0,
                    'delete'
                    )
    else:
        message = """something whent wrong.
                     We cold not empty your cart. """
    order = Order.objects.get(id=order_id)
    order_positions = OrderPosition.objects.filter(order=order_id)
    if (order_positions.count()) > 0:
        order_position_list = list(order_positions)
        for idx, order_position in enumerate(order_positions):
            # get currencyname to display:
            if order.exchange_rate is not None:
                # get price of position in order and append to a list:
                rate = ExchangeRate.objects.get(id=order.exchange_rate.id)
                price = round(
                    rate.exchange_rate_to_chf * order_position.price_in_chf,
                    2)
                currency_name = order.exchange_rate.name
            else:
                currency_name = 'CHF'
                price = order_position.price_in_chf
            order_position_list[idx] = order_position
            price_list.append(price)
            totalprice_list.append(price)
        total = sum(totalprice_list)
        order_position_list_zip = zip(order_position_list,
                                      price_list,
                                      totalprice_list)
    return render(request, 'webshop/order.html', {
                  'order': order,
                  'order_position_list_zip': order_position_list_zip,
                  'total': total,
                  'currency_name': currency_name,
                  'category_list': category_list,
                  })
