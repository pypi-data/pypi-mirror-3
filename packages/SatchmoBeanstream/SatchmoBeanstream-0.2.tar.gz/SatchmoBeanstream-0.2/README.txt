"""
SatchmoBeanstream module currently only support Purchase transactions.

We're not using LiveSettings for storing Credentials, because Livesettings should be disabled in production anyways, so store the Beanstream credentials in your SETTINGS.py file instead, with the following syntax:

BEANSTREAM_CREDENTIALS = {
   'username' : 'MY_USER',
   'password' : 'MY_PASS',
   'merchant_id' : 'MY_MERCHANT_ID'
   }

How to install:
pip install SatchmoBeanstream

Add it to installed apps in your settings file.:

"""
INSTALLED_APPS = (
    #....
    'payment',
    'stchmobeanstream.beanstream',
    #....
)
"""

Add the settings to livesettings:
** Note, you can use the livesettings DB storage if you wish, but I recommend using 'DB': False and setting the livesettings manually in the settings.py file instead.
** NOTE2, important! 'LIVE' option does nothing right now (in the satchmobeanstream module anyways...), so if you specify production credentials in BEANSTREAM_CREDENTIALS, it will start charging real money, if you use test credentials, it will do test transactions.
"""

LIVESETTINGS_OPTIONS = {
    1 : {  # Your site ID
        #....
        'SETTINGS' : {
            'PAYMENT_BEANSTREAM' : {
                'CREDITCHOICES' : '[\"Visa\", \"Mastercard\"]',
                'LIVE': 'True',
                'ORDER_EMAIL_OWNER': 'True',
                'ORDER_EMAIL_EXTRA': 'myemail@derp.com',
            },
        },	       
    },
}

"""
Testing:

Create a test_settings.py and specify your test credentials from beanstream in there, then:

./manage.py test satchmobeanstream.beanstream --settings=test_settings --nologcapture -s

Note: You may get an error from suds that look like this:

  File "<some path>/site-packages/suds/sax/document.py", line 48, in str
    s.append(self.root().str())
AttributeError: 'NoneType' object has no attribute 'str'
Logged from file core.py, line 73

Don't worry about it, i'm still not sure why, but the SOAP transaction DOES happen if the test passes.
"""
