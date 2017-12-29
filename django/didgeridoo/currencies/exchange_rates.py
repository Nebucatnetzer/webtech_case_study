from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

today = datetime.now().strftime("%Y-%m-%d")

""" this method calls a rss/XML Resource
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
    SNB_URL = 'https://www.snb.ch/selector/de/mmr/exfeed/rss'
    urlsocket = urllib.request.urlopen(SNB_URL)
    root = ET.parse(urlsocket)
    root = ET.ElementTree(root)

    # ~~~~~~~~~~~~~~~~~~~~~
    # development block:
    # ~~~~~~~~~~~~~~~~~~~~~
    # root = ET.ElementTree(file='rss')
    # ~~~~~~~~~~~~~~~~~~~~~
    # Namespaces
    ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
          'none': 'http://purl.org/rss/1.0/',
          'dc': 'http://purl.org/dc/elements/1.1/',
          'dcterms': 'http://purl.org/dc/terms/',
          'cb': 'http://www.cbwiki.net/wiki/index.php/Specification_1.2/'
          }
    # Pathvariables to XML Namespaces
    none_path = 'none:item/'
    rate_path = 'cb:statistics/cb:exchangeRate/'
    observation_path = 'cb:statistics/cb:exchangeRate/cb:observation/'
    # THE FILE DATE:
    xml_datetime_string = root.find('none:channel/dcterms:created', ns).text
    # because of few knowlede just trim end of string to avoid error
    xml_datestring = xml_datetime_string.split('T')[0]
    # parse string to date object:
    xml_date = datetime.date(datetime.strptime(xml_datestring, "%Y-%m-%d"))
    exchange_rates = {}
    for item in root.findall('none:item', ns):
        # THE CURRENCY DATE:
        datetime_str = item.find('dc:date', ns).text
        # convert string to date object:
        # https://stackoverflow.com/a/12282040/4061870
        # seams like snb striked the microsecond somewhere between Nov. and
        # Dez. 2017 so maybe first check time type. "%Y-%m-%dT%H:%M:%S.%f%z"
        date = datetime.strptime(''.join(
                                 datetime_str.rsplit(':', 1)),
                                 "%Y-%m-%dT%H:%M:%S%z").strftime(
                                 "%Y-%m-%d")
        # only the values of today are used so check for date in XML:
        if date == today:
            title = item.find('none:title', ns).text
            base_currency = item.find(rate_path +
                                      'cb:baseCurrency', ns).text
            target_currency = item.find(rate_path +
                                        'cb:targetCurrency', ns).text
            CHFvalue = float(item.find(observation_path +
                                       'cb:value', ns).text)
            CHFvalue = float(CHFvalue)  # convert to float
            FOREIGNvalue = CHFvalue  # copy to new value to have both.
            unit = item.find(observation_path + 'cb:unit', ns).text
            decimals = int(item.find(observation_path +
                                     'cb:decimals', ns).text)
            # because it's dangerous to check for present, i check for none
            # here and have to do something in there so i set the target to 0.
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
            FOREIGNvalue = 1 / CHFvalue
            FOREIGNvalue *= unit_mult
            CHFvalue = CHFvalue / unit_mult
            # truncate it to decimal values provided by the xml:
            FOREIGNvalue_round = round(FOREIGNvalue, 5)
            # Print nice setup of all calculated currencys for Dev:
            # print("date:", date, " 1 ", target_currency, " costs: ",
            #       CHFvalue, "CHF and 1 ", base_currency, " costs: ",
            #       FOREIGNvalue_round, target_currency)
            exchange_rates.update(
                {target_currency: FOREIGNvalue_round})
            # Print the Dictionary:
            # print(exchange_rates)
        else:
            break
    return(exchange_rates, date)
    # for development its preferable to see that the for loop is done:
    # print('no more fresh data!')
