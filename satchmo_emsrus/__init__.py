# -*- coding: utf-8 -*-
from models import Shipper
from satchmo_utils import load_once

load_once('satchmo_emsrus', 'satchmo_emsrus')
def get_methods():
    return [Shipper()]
