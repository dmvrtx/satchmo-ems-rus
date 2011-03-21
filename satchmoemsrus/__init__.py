# -*- coding: utf-8 -*-
from models import Shipper
from satchmo_utils import load_once

load_once('satchmoemsrus', 'satchmoemsrus')
def get_methods():
    return [Shipper()]
