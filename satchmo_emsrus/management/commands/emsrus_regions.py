# -*- coding: utf-8 -*-
u"""Команда замены списка российских регионов"""

from django.core.management.base import BaseCommand, CommandError
from urllib2 import urlopen
from l10n.models import Country, AdminArea
import json

class Command(BaseCommand):
    args = None
    help = 'Replace Russian areas with those from EMS Russia API'

    def clean_name(self, name):
        return name.strip('* \t\r\n')

    def handle(self, *args, **options):
        u"""Замена списка областей России на EMS"""
        country = Country.objects.filter(iso2_code='RU').all()
        if len(country):
            # Россию нашли
            country = country[0]

            # теперь регионы
            response = json.load(urlopen('http://emspost.ru/api/rest/?method=ems.get.locations&type=regions&plain=true'))
            # удаляем старые
            regions = AdminArea.objects.filter(country=country).delete()
            for loc in response['rsp']['locations']:
                row = AdminArea(country=country, name=self.clean_name(loc['name']))
                row.save()
            self.stdout.write('%d region(s) retrieved\n' % (
                len(response['rsp']['locations']),))

