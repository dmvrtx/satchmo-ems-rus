# -*- coding: utf-8 -*-
u"""Проверка поиска региона EMS по списку контактов"""

from django.core.management.base import BaseCommand, CommandError
from satchmo_emsrus.models import Location
from satchmo_store.contact.models import Contact

class Command(BaseCommand):
    args = None
    help = 'Checks EMS locations for contacts'

    def handle(self, *args, **options):
        # сохраним все локации, чтобы не ходить по кругу каждый раз
        for contact in Contact.objects.all():
            address = contact.shipping_address
            if address:
                self.stdout.write('ADDRESS: %r\n' % (address,))
                self.stdout.write((u'%s (%s)\t%s\t%s\t%s\n' % (
                        address.country, address.country.iso2_code,
                        address.state, address.city,
                        self.find_location(address))).encode('utf-8'))

    def find_location(self, address):
        u"""Поиск локации EMS по адресу"""
        if not hasattr(self, 'locations'):
            self.locations = list(Location.objects.all().order_by('-kind'))
        for location in self.locations:
            if location.check_address(address):
                return '%s (%s)' % (location.name, location.kind)
        return 'not found'

