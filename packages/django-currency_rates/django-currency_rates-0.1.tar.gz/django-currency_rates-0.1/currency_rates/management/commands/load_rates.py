import json
import urllib2
import datetime
from decimal import Decimal
from django.core.management.base import NoArgsCommand
from currency_rates.models import Currency, ExchangeRate

CURRENT_RATES_URL = "http://openexchangerates.org/latest.json"


class Command(NoArgsCommand):
        help = "Get the current rates from %s" % CURRENT_RATES_URL

        def handle_noargs(self, **options):

            base_currency = 'EUR'

            f = urllib2.urlopen(CURRENT_RATES_URL)
            data = json.loads(f.read())

            base_currency_rate = Decimal(str(data['rates'][base_currency]))

            conversion = lambda x: Decimal(str(x)) / base_currency_rate
            date = datetime.date.fromtimestamp(data['timestamp'])

            ExchangeRate.objects.filter(date=date).delete()

            for code, rate in data['rates'].iteritems():
                try:
                    currency = Currency.objects.get(code=code)
                except Currency.DoesNotExist:
                    continue
                ExchangeRate.objects.create(currency=currency,
                                date=date, rate=conversion(rate))
