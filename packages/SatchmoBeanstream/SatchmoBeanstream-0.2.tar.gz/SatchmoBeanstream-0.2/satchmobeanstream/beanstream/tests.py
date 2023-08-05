import random
from decimal import Decimal

from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.core.urlresolvers import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.conf import settings

from l10n.models import *
from livesettings import config_get, config_get_group
from payment import utils
from product.models import *
from satchmo_store.contact.models import *
from satchmo_store.shop.models import *
from satchmo_utils.dynamic import lookup_template, lookup_url
from payment.urls import make_urlpatterns
from keyedcache import cache_delete
from satchmo_store.shop import get_satchmo_setting, signals
from payment.models import CreditCardDetail
from satchmo_store.shop.models import OrderPayment, OrderAuthorization
import keyedcache

settings.LIVESETTINGS_OPTIONS = LIVESETTINGS_OPTIONS = {
    1 : {
        'DB' : False,
        'SETTINGS' : {
            'PAYMENT_BEANSTREAM' : {
                'CREDITCHOICES' : '[\"Visa\", \"Mastercard\"]',
                'LIVE': 'True',
                'ORDER_EMAIL_OWNER': 'True',
                'ORDER_EMAIL_EXTRA': 'info@nothing.com',
                },
            'PAYMENT' : {
                'CREDITCHOICES' : '[\"Visa\", \"Mastercard\"]',
                'LIVE': 'True',
                'ORDER_EMAIL_OWNER': 'True',
                'ORDER_EMAIL_EXTRA': 'info@nothing.com',
                },
            'SHIPPING' : {
                'MODULES' : '[\"flat\"]',
                },
            'TAX' : {
                'MODULE' : 'tax.modules.no',
                },
            'PRODUCT': {
                'NO_STOCK_CHECKOUT': 'True',
                },
            },
        },
    }


def get_step1_post_data(CA):
    return {
        'email': 'john.doe@pranana.com',
        'first_name': 'John',
        'last_name' : 'Doe',
        'phone': '514-666-6666',
        'street1': '3381 Steeles Avenue East',
        'city': 'North York',
        'state': 'ON',
        'postal_code': 'M2H3S7',
        'country': CA.pk,
        'ship_street1': '3381 Steeles Avenue East',
        'ship_city': 'North York',
        'ship_state': 'ON',
        'ship_postal_code': 'M2H4F1',
        'paymentmethod': 'PAYMENT_BEANSTREAM',
        'copy_address' : True
        }

domain = 'http://example.com'
prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''

def make_some_order(country, state, site=None, orderitems=None):
    if not orderitems:
        orderitems = [('dj-rocks', 1), ]

    if not site:
        site = Site.objects.get_current()

    c = Contact(first_name="Order", last_name="Tester",
        role=ContactRole.objects.get(pk='Customer'), email="order@example.com")
    c.save()
    phone = PhoneNumber(primary=True, contact_id=c.id, phone='514-555-5555')
    phone.save()

    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact = country)

    ad = AddressBook(contact=c, description="home",
        street1 = "test", state=state, city="Montreal",
        country = country, is_default_shipping=True,
        is_default_billing=True)
    ad.save()
    
    o = Order(
        contact=c,
        shipping_cost=Decimal('1.00'),
        site = site,
        id=random.randint(1000,100000),
        bill_addressee = 'John Doe',
        bill_postal_code = 'H2T1N6',
        bill_state = 'QC',
        bill_street1 = '123 Happy St.',
        bill_country = 'CA',
        bill_city = 'Montreal',
        )
    o.save()

    for slug, qty in orderitems:
        p = Product.objects.get(slug=slug)
        price = p.unit_price
        item = OrderItem(order=o, product=p, quantity=qty,
            unit_price=price, line_item_price=price*qty)
        item.save()

    return o


class TestModulesSettings(TestCase):

    def setUp(self):
        self.beanstream = config_get_group('PAYMENT_BEANSTREAM')

    def tearDown(self):
        keyedcache.cache_delete()

    def testGetBeanstream(self):
        self.assert_(self.beanstream != None)
        self.assertEqual(self.beanstream.LABEL, 'Live Credit Card Processing')

    def testLookupTemplateSet(self):
        t = lookup_template(self.beanstream, 'test.html')
        self.assertEqual(t, 'test.html')

    def testLookupURL(self):
        try:
            t = lookup_url(self.beanstream, 'test_doesnt_exist')
            self.fail('Should have failed with NoReverseMatch')
        except urlresolvers.NoReverseMatch:
            pass

    def testUrlPatterns(self):
        pats = make_urlpatterns()
        self.assertTrue(len(pats) > 0)


class TestPaymentHandling(TestCase):
    fixtures = ['l10n_canada_only.json', 'store-data.yaml', 'beanprods.yaml', 'initial_data.yaml']

    def setUp(self):
        self.client = Client()
        self.CA = Country.objects.get(iso2_code__iexact = "CA")

    def tearDown(self):
        keyedcache.cache_delete()


    def test_capture(self):
        """Test making a capture without authorization using BEANSTREAM."""
        order = make_some_order(self.CA, '')
        self.assertEqual(order.balance, order.total)
        self.assertEqual(order.total, Decimal('9.00'))

        processor = utils.get_processor_by_key('PAYMENT_BEANSTREAM')
        pendingpayment = processor.create_pending_payment(order=order, amount=order.total)
        
        op = pendingpayment.capture

        cc = CreditCardDetail(
            orderpayment=op,
            credit_type='Visa',
            expire_month=12,
            expire_year=2015,
            )
        cc.storeCC('4030000010001234')
        cc.setCCV('123')
        cc.save()

        processor.prepare_data(order)
        result = processor.capture_payment()

        self.assertEqual(result.success, True)
        pmt1 = result.payment
        self.assertEqual(type(pmt1), OrderPayment)

        self.assertEqual(result.success, True)
        payment = result.payment
        self.assertEqual(pmt1, payment)
        self.assertEqual(order.orderstatus_set.latest().status, 'New')
        self.assertEqual(order.authorized_remaining, Decimal('0'))
        self.assertEqual(order.balance, Decimal('0'))
