"""Simple wrapper for standard checkout as implemented in payment.views"""

from django.views.decorators.cache import never_cache
from livesettings import config_get_group
from payment.views import confirm, payship
    
beanstream = config_get_group('PAYMENT_BEANSTREAM')
    
def pay_ship_info(request, SSL=False):
    return payship.credit_pay_ship_info(request, beanstream)
pay_ship_info = never_cache(pay_ship_info)
    
def confirm_info(request, SSL=False):
    return confirm.credit_confirm_info(request, beanstream)
confirm_info = never_cache(confirm_info)

