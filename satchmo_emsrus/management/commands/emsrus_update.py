# -*- coding: utf-8 -*-
u"""Команда загрузки списка стран/городов/регионов"""

from django.core.management.base import BaseCommand, CommandError
from satchmo_emsrus.models import Location
from urllib2 import urlopen
import json

class Command(BaseCommand):
    args = None
    help = 'Retrieves and stores locations from EMS Russia API'

    def clean_name(self, name):
        return name.strip('* \t\r\n')

    def handle(self, *args, **options):
        u"""Загрузка и обработка списка локаций"""
        # сначала страны
        response = json.load(urlopen('http://emspost.ru/api/rest/?method=ems.get.locations&type=countries&plain=true'))
        for loc in response['rsp']['locations']:
            row = Location(key=loc['value'], name=self.clean_name(loc['name']), kind='C')
            row.save()
        self.stdout.write('%d country(ies) retrieved\n' % (
            len(response['rsp']['locations']),))

        # теперь регионы
        response = json.load(urlopen('http://emspost.ru/api/rest/?method=ems.get.locations&type=regions&plain=true'))
        for loc in response['rsp']['locations']:
            row = Location(key=loc['value'], name=self.clean_name(loc['name']), kind='R')
            row.save()
        self.stdout.write('%d region(s) retrieved\n' % (
            len(response['rsp']['locations']),))

        # теперь города
        response = json.load(urlopen('http://emspost.ru/api/rest/?method=ems.get.locations&type=cities&plain=true'))
        for loc in response['rsp']['locations']:
            row = Location(key=loc['value'], name=self.clean_name(loc['name']), kind='T')
            row.save()
        self.stdout.write('%d city(ies) retrieved\n' % (
            len(response['rsp']['locations']),))

