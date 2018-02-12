from webshop.models import (Article,
                            Category,
                            ArticleStatus)

from currencies.models import ExchangeRate, ExchangeRate_name
from currencies.forms import CurrenciesForm

def process_article_prices(request, articles):
    articles_list = list(articles)
    rate = ExchangeRate
    currency_name = "CHF"

    if not 'currency' in request.session:
        request.session['currency'] = None
        return {'request':request,
                'currency_name':currency_name,
                'articles_list':articles_list}

    if request.method == 'POST':
        currencies_form = CurrenciesForm(request.POST)
        if currencies_form.is_valid():
            cf = currencies_form.cleaned_data
            if cf['currencies']:
                selection = cf['currencies']
                request.session['currency'] = selection.id
                currency_name = ExchangeRate_name.objects.get(id=selection.id)
            else:
                request.session['currency'] = None
                return {'request':request,
                        'currency_name':currency_name,
                        'articles_list':articles_list}

    if request.session['currency']:
        currency = request.session['currency']
        for idx, article in enumerate(articles_list):
            article.price_in_chf = rate.exchange(currency, article.price_in_chf)
            articles_list[idx] = article
            currency_name = ExchangeRate_name.objects.get(id=currency)
        return {'request':request,
                'articles_list':articles_list,
                'currency_name':currency_name}

    return {'request':request,
            'currency_name':currency_name,
            'articles_list':articles_list}


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
