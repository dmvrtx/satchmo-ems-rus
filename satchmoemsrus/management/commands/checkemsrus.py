# -*- coding: utf-8 -*-
u"""Проверка поиска региона EMS по списку контактов"""

from django.core.management.base import BaseCommand, CommandError
from satchmoemsrus.models import Location
from satchmo_store.contact.models import Contact

class Command(BaseCommand):
    args = None
    help = 'Checks EMS locations for contacts'

    def handle(self, *args, **options):
        for contact in Contact.all():
            with contact.shipping_address as address:
