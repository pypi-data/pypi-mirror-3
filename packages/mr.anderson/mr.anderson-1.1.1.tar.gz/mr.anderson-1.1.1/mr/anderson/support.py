# -*- coding: utf-8 -*-
import os
import logging

logging.basicConfig()
logger = logging.getLogger('mr.anderson')

here = os.path.abspath(os.path.dirname(__file__))
STATIC = os.path.join(here, 'static')
TEMPLATES = os.path.join(here, 'templates')
