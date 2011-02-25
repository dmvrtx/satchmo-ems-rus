# -*- coding: utf-8 -*-
u"""
Модели для EMS
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from shipping.modules.base import BaseShipper
import logging
import datetime

log = logging.getLogger('satchmo-ems-rus')

class Location(models.Model):
    u"""Представление области в которую может доставить EMS"""

    LOCATION_KINDS = (
            ('C', _('Country')),
            ('R', _('Region')),
            ('T', _('Town'))
            )

    key = models.SlugField(_('Key'))
    kind = models.CharField(_('Type'), max_length=1, choices=LOCATION_KINDS)
    name = models.CharField(_('Name'), max_length=128)

class Shipper(BaseShipper):
    u"""Метод отправки EMS"""

    def __str__(self):
        return 'EMS Russia shipper'

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
