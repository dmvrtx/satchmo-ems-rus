# -*- coding: utf-8 -*-
u"""Админские настройки для EMS-доставки"""

from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('satchmoemsrus', 'EMS Russia'))

SHIPPING_GROUP = ConfigurationGroup('satchmoemsrus',
    _('EMS Russia Shipping Settings'),
    requires = SHIP_MODULES,
    ordering = 101)

config_register_list(
    StringValue(SHIPPING_GROUP,
        'CITY_FROM',
        description=_("Origin city"),
        help_text=_("City of origin for parcels."),
        default=u""),
)
