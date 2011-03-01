# -*- coding: utf-8 -*-
u"""
Модели для EMS
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from shipping.modules.base import BaseShipper
import datetime
import logging
import re

log = logging.getLogger('satchmo-ems-rus')

STRIP_JUNK = re.compile(r'[ -=+\r\n\t]')

def is_similiar(str1, str2):
    u"""Определение схожести строк"""
    sub = STRIP_JUNK.sub('', str1.lower())
    lookup = STRIP_JUNK.sub('', str2.lower())
    while sub:
        if lookup.find(sub) > -1:
            break
        if (len(sub) % 2):
            sub = sub[:-1]
        else:
            sub = sub[1:]
    if sub and ((float(len(sub)) / len (str1)) > 0.6):
        return True
    return False

class Location(models.Model):
    u"""Представление области в которую может доставить EMS"""

    LOCATION_KINDS = (
            ('C', _('Country')),
            ('R', _('Region')),
            ('T', _('Town'))
            )

    key = models.SlugField(_('Key'), primary_key=True)
    kind = models.CharField(_('Type'), max_length=1, choices=LOCATION_KINDS)
    name = models.CharField(_('Name'), max_length=128)

    def check_address(self, address):
        u"""Проверка данных адреса (класс AddressBook) на соответствие местоположению"""
        if (self.kind == 'C') \
                and ((address.country.iso2_code == self.key) \
                or is_similiar(address.country.name, self.name)):
                    return True
        if (self.kind == 'R') \
                and is_similiar(address.state, self.name):
                    return True
        if (self.kind == 'T') \
                and is_similiar(address.city, self.name):
                    return True
        return False

class Shipper(BaseShipper):
    u"""Метод отправки EMS"""

    def __str__(self):
        return 'EMS Russia shipper'

    @property
    def locations(self):
        # обновим кэш, если пришло время
        if (not hasattr(self, '_locations_expires')) \
                or (datetime.datetime.now() > self._locations_expires):
            self._locations = list(Location.objects.all().order_by('-kind'))
            self._locations_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
        return self._locations

    def description(self):
        return _('Shipping by EMS Russia')

    def valid(self, order=None):
        u"""Проверка возможности доставки"""
        if order:
            products = order.orderitem_set.all()
            # TODO: проверка адреса
        elif self.cart:
            products = self.cart.cartitem_set.all()
            pass

        for cartitem in self.cart.cartitem_set.all():
            p = cartitem.product
            if not p.is_shippable:
                return False
        return True

    def _get_location(self, contact):
        u"""Вытаскивает локацию к которой привязан контакт"""
        raise NotImplementedError
