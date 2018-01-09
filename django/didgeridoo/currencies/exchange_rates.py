from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import datetime as dt


"""
this method calls a rss/XML Resource
of Currency's and parses it to our
needed exchange rate values.
The return is a dictionary carring
Key:Value pairs of new currencys.
"""


def get_exchange_rate():
    # During weekends there are no updates.
    # To develop i need a testresource.
    # In that case i comment the Online Resource block and uncomment the
    # development Block...

    # ~~~~~~~~~~~~~~~~~~~~~
    # Online Resource block:
    # ~~~~~~~~~~~~~~~~~~~~~
    today = datetime.now().strftime("%Y-%m-%d")
    SNB_URL = 'https://www.snb.ch/selector/de/mmr/exfeed/rss'
    urlsocket = urllib.request.urlopen(SNB_URL)
    root = ET.parse(urlsocket)
    root = ET.ElementTree(root)

    # ~~~~~~~~~~~~~~~~~~~~~
    # development block:
    # ~~~~~~~~~~~~~~~~~~~~~
    # today = "2018-01-03"
    # try:
    #     root = ET.ElementTree(file='rss')
    # except Exception as e:
    #     print('exchange_rates.py_urlsocket failed %s (
    #           %s) on date: %s for %s'
    #           % (e, type(e), root))
    # ~~~~~~~~~~~~~~~~~~~~~

    # Namespaces
    ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
          'none': 'http://purl.org/rss/1.0/',
          'dc': 'http://purl.org/dc/elements/1.1/',
          'dcterms': 'http://purl.org/dc/terms/',
          'cb': 'http://www.cbwiki.net/wiki/index.php/Specification_1.2/'
          }
    # Pathvariables to XML Namespaces
    rate_path = 'cb:statistics/cb:exchangeRate/'
    observation_path = 'cb:statistics/cb:exchangeRate/cb:observation/'
    exchange_rates = {}
    for item in root.findall('none:item', ns):
        # THE CURRENCY DATE:
        datetime_str = item.find('dc:date', ns).text
        # convert string to date object:
        # https://stackoverflow.com/a/12282040/4061870
        # seams like snb striked the microsecond somewhere between Nov. and
        # Dez. 2017 so maybe first check time type is with milliseconds:
        try:
            date = datetime.strptime(''.join(
                         datetime_str.rsplit(':', 1)),
                         "%Y-%m-%dT%H:%M:%S%z").strftime(
                         "%Y-%m-%d")
        except:
            try:
                date = datetime.strptime(''.join(
                             datetime_str.rsplit(':', 1)),
                             "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                             "%Y-%m-%d")
            except Exception as e:
                print('%s (%s)' % (e, type(e)))
        # Print dates for development:
        # print("date:", date, "today:", today)
        # only the values of today are used so check for date in XML:
        if date == today:
            target_currency = item.find(rate_path +
                                        'cb:targetCurrency', ns).text
            value = float(item.find(observation_path +
                                    'cb:value', ns).text)
            value = float(value)  # convert to float
            foreign_value = value  # copy to new value to have both.
            # because it's dangerous to check for present, i check for none
            # here and have to do something in there so i set the target to 1.
            if item.find(observation_path + 'cb:unit_mult', ns) is None:
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
            # Print nice setup of all calculated currencys for Dev:
            # print("date:", date, " 1 ", target_currency, " costs: ",
            #       CHFvalue, "CHF and 1 ", base_currency, " costs: ",
            #       FOREIGNvalue_round, target_currency)
            exchange_rates.update(
                {target_currency: foreign_value_round})
            # Print the Dictionary:
            # print(exchange_rates)
        else:
            exchange_rates = "SNB did not update the currencies for today."
    return(exchange_rates, today)

    # for development its preferable to see that the for loop is done:
    # print('no more fresh data!')
