from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

"""
this method calls a rss/XML Resource
of Currency's and parses it to our
needed exchange rate values.
The return is a dictionary carring
Key:Value pairs of new currencys.
"""


def get_rss(url):
    urlsocket = ''
    try:
        urlsocket = urllib.request.urlopen(url)
        return(urlsocket)
    except urllib.error.URLError as e:
        print('err: urllib.request.urlopen: ', e.reason)


def parse_rss(urlsocket):
    rss_tree = ''
    if urlsocket:
        root = ET.parse(urlsocket)
        rss_tree = ET.ElementTree(root)
    return(rss_tree)


def pass_local_file():
    rss_tree = ET.ElementTree(file='rss')
    return(rss_tree)


def get_exchange_rate(rss_tree, ns):
    # Pathvariables to XML Namespaces with
    rate_path = 'cb:statistics/cb:exchangeRate/'
    observation_path = 'cb:statistics/cb:exchangeRate/cb:observation/'
    exchange_rates = []

    for item in rss_tree.findall('none:item', ns):
        datetime_str = item.find('dc:date', ns).text
        try:
            date = datetime.strptime(''.join(
                         datetime_str.rsplit(':', 1)),
                         "%Y-%m-%dT%H:%M:%S%z").strftime(
                         "%Y-%m-%d")
        except Exception as e:
            print('%s (%s)' % (e, type(e)))
            try:
                date = datetime.strptime(''.join(
                             datetime_str.rsplit(':', 1)),
                             "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                             "%Y-%m-%d")
                continue
            except Exception as e:
                print('%s (%s)' % (e, type(e)))
                continue
        # now search for the currency exchange rate:
        target_currency = item.find(rate_path +
                                    'cb:targetCurrency', ns).text
        value = float(item.find(observation_path +
                                'cb:value', ns).text)
        value = float(value)  # convert to float
        foreign_value = value  # copy to new value to have both.

        if item.find(observation_path + 'cb:unit_mult', ns) is None:
            # because it's dangerous to check for present,
            # i check for none here and have to set the target
            # to 1. as im multiplying it later.
            unit_mult = float("1.0")
        else:
            # shift left by 2 digits with "/"
            # https://stackoverflow.com/questions/8362792/
            # because some currencys differ widly from CHF
            unit_mult = item.find(observation_path +
                                  'cb:unit_mult', ns).text
            # unit_mult defaults to '0' so we check for 8 decimal
            # values (2..-6) they represent the fracton value to
            # calculate the correct decimalpoint.
            if unit_mult == '2':  # thinking of Bitcoins
                unit_mult = '0.01'
            if unit_mult == '1':
                unit_mult = '0.10'
            if unit_mult == '-1':
                unit_mult = '10'
            if unit_mult == '-2':  # Japan Yen
                unit_mult = '100'
            if unit_mult == '-3':
                unit_mult = '1000'
            if unit_mult == '-4':
                unit_mult = '10000'
            if unit_mult == '-5':
                unit_mult = '100000'
            if unit_mult == '-6':  # indian rupies
                unit_mult = '1000000'
            unit_mult = float(unit_mult)  # convert to float
        # calculate the Currency to CHF:
        foreign_value = 1 / value
        foreign_value *= unit_mult
        value = value / unit_mult
        # truncate it to decimal values provided by the xml:
        foreign_value_round = round(foreign_value, 5)
        # Print nice setup of all calculated currencys for development:
        # print("date:", date, " 1 ", target_currency, " costs: ",
        #       CHFvalue, "CHF and 1 ", base_currency, " costs: ",
        #       FOREIGNvalue_round, target_currency)
        data = [{'date': date,
                 'currency': target_currency,
                 'exchangerate': foreign_value_round}]
        exchange_rates.append(data)
        # Print the Dictionary:
    return(exchange_rates)
