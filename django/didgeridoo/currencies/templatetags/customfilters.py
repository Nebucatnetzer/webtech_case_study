from django import template


register = template.Library()


@register.filter()
def boldcoffee(value):
    # currency_of_customer = request.session['currency']
    return '%s !!gefiltert!!' % value

    # excample filter: {{ article.price_in_chf|boldcoffee }}
