# -*- coding: utf-8 -*-
u"""
Класс доставки
"""

from decimal import Decimal
from django.utils.translation import ugettext as _
from livesettings import config_get_group, config_value
from satchmo_emsrus.models import Location, is_similiar
from shipping.modules.base import BaseShipper
from urllib2 import urlopen

import datetime
import logging
import json

log = logging.getLogger('satchmo-ems-rus')

class Shipper(BaseShipper):
    u"""Метод отправки EMS"""

    def __init__(self, cart=None, contact=None):
        u"""Инициализация"""
        self.cart = cart
        self.contact = contact
        self.id = u'EMSRussianPost'

        self.__locations_expires = None
        self.__locations = None

        self._charges = None
        self._delivery_days = None

        self._city_from = ''
        # поиск города из конфигурации
        self._settings = config_get_group('satchmo_emsrus')
        if self._settings.CITY_FROM:
            for location in self.locations:
                if (location.kind == 'T') and is_similiar(unicode(location.name), unicode(self._settings.CITY_FROM)):
                    self._city_from = location.key

        if self.cart and self.contact:
            self.calculate()

    def __str__(self):
        return 'EMS Russia shipper'

    def description(self):
        u"""Описание метода доставки"""
        return _('Express shipping')

    def method(self):
        u"""
        Описание метода доставки
        """
        return _("EMS Russia")

    def expectedDelivery(self):
        u"""
        Дата доставки
        """
        if self._delivery_days is not None:
            if self._delivery_days != "1":
                return _("in %s business days" % self._delivery_days)
            else:
                return _("in %s business day" % self._delivery_days)
        else:
            return _("in 7-14 business days")

    @property
    def locations(self):
        u"""Список доступных местоположений"""
        # обновим кэш, если пришло время
        if (self.__locations_expires is None) \
                or (datetime.datetime.now() > self.__locations_expires):
            self.__locations = list(Location.objects.all().order_by('-kind'))
            self.__locations_expires = datetime.datetime.now() \
                    + datetime.timedelta(hours=1)
        return self.__locations

    def valid(self, order=None):
        u"""Проверка возможности доставки"""

        if float(Decimal(str(self._settings.DEFAULT_FEE))):
            # если есть такса по умолчанию - значит не надо ничего перепроверять
            return True

        products = []
        if order:
            products = order.orderitem_set.all()
            location = None
            for loc in self.locations:
                if loc.check_order(order):
                    location = loc
                    break
            if location is None:
                log.info('Couldn\'t find location for order %s.' % (order.pk,))
                return False
            else:
                log.info('Order %s is set to location %s' % (order.pk, location))
        elif self.cart:
            # если в корзине указан контакт клиента - проверим его доступность
            if (self.cart.customer is not None) \
                    and (self.get_location(self.cart.customer) is None):
                return False
            products = self.cart.cartitem_set.all()

        for cartitem in products:
            # проверим все ли товары имеют указанный вес и должны доставляться?
            if not (cartitem.product.is_shippable and \
                    cartitem.product.smart_attr('has_full_weight')):
                return False
        return True

    def product_weight_kg(self, product):
        u"""
        Вычислить вес продукта в кг
        """
        weight = Decimal('0.0')
        if product.smart_attr('has_full_weight'):
            weight = product.smart_attr('weight')
            if product.smart_attr('weight_units') == 'lb':
                weight = weight * 0.45359237
        return weight

    def get_location(self, contact):
        u"""
        Поиск местоположения контакта
        """
        for location in self.locations:
            if location.check_address(contact.shipping_address):
                return location
        return None

    def cost(self):
        assert(self._calculated)
        cost = Decimal(self._charges)
        if cost and self._settings.HANDLING_FEE:
            cost = cost + Decimal(str(self._settings.HANDLING_FEE))
        return cost

    def calculate(self, cart, contact):
        u"""
        Подсчёт стоимости доставки
        """
        self.cart = cart
        self.contact = contact
        location = self.get_location(self.contact)
        if location is not None:
            # считаем вес
            weight = Decimal('0.0')
            for cartitem in self.cart.cartitem_set.all():
                p_weight = self.product_weight_kg(cartitem.product)
                if p_weight is not None:
                    weight += p_weight * cartitem.quantity

            # если вес меньше чем минимальный - используем минимальный
            if weight < Decimal(str(self._settings.MIN_WEIGHT)):
                weight = Decimal(str(self._settings.MIN_WEIGHT))

            try:
                request_url = 'http://emspost.ru/api/rest/' \
                        '?method=ems.calculate&type=att&to=%s&weight=%0.2f' % (
                            location.key, weight)
                if location.kind != 'C':
                    request_url = '%s&from=%s' % (request_url, self._city_from)
                log.info('EMS API request: %s' % (request_url,))
                response = json.load(urlopen(request_url))
                if response['rsp']['stat'] == 'ok':
                    if ('term' in response['rsp']) and ('max' in response['rsp']['term']):
                        self._delivery_days = response['rsp']['term']['max']
                    self._charges = response['rsp']['price']
                    self._calculated = True
                else:
                    # не удалось рассчитать
                    log.error('EMS Response: (%s) %s' % (response['rsp']['err']['code'],
                        response['rsp']['err']['msg']))
            except:
                pass
        else:
            log.info('Couldn\'t find EMS location for contact %s' % (contact.id,))
        if (self._charges is None) and float(Decimal(str(self._settings.DEFAULT_FEE))):
            # воспользуемся тарифом по умолчанию
            self._charges = str(self._settings.DEFAULT_FEE)
            self._calculated = True

