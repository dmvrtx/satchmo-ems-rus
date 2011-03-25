# -*- coding: utf-8 -*-
u"""
Модели для EMS
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _
import re

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

    def __str__(self):
        u"""Строковое представление"""
        return '%s (%s)' % (self.name, self.kind)

    def __repr__(self):
        u"""Представление модели"""
        return 'Location %s (%s)' % (self.key, self.kind)

    def check_address(self, address):
        u"""Проверка данных адреса (класс AddressBook) на
            соответствие местоположению"""
        if (self.kind == 'C') \
                and ((address.country.iso2_code.lower() == self.key.lower()) \
                or is_similiar(address.country.name, self.name)):
            return True
        if address.country.iso2_code.lower() == 'ru':
            # регионы следует искать только для россии
            if (self.kind == 'R') \
                    and is_similiar(address.state, self.name):
                return True
            if (self.kind == 'T') \
                    and is_similiar(address.city, self.name):
                return True
        return False

    def check_order(self, order):
        u"""Проверка данных по объекту заказа"""
        if order.ship_street1:
            # вроде бы есть адрес в заказе
            if (self.kind == 'C') \
                    and (order.ship_country.lower() == self.key):
                return True
            if (order.ship_country.lower() == 'ru'):
                # регионы ищем только внутри России
                if (self.kind == 'R') \
                        and is_similiar(order.ship_state, self.name):
                    return True
                if (self.kind == 'T') \
                        and is_similiar(order.ship_city, self.name):
                    return True
        elif (order.contact is not None):
            # иначе вернём результат проверки по контакту
            return self.check_address(order.contact.shipping_address)
        return False

