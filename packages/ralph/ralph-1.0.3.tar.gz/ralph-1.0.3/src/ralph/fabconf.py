#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 by AllegroGroup

# INTERNAL ALLEGRO CONFIGURATION FOR FABRIC, DO NOT DISTRIBUTE.
# INTERNAL ALLEGRO CONFIGURATION FOR FABRIC, DO NOT DISTRIBUTE.
# INTERNAL ALLEGRO CONFIGURATION FOR FABRIC, DO NOT DISTRIBUTE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals




PROD_HOSTS = ('s10335.dc2', 's10337.dc2', 's10276.dc2', 's20960.dc3',
              'ralph01.te2', '10.193.6.152')
#DEV_HOSTS = ('ralph02.te2', 'ralph03.te2')
DEV_HOSTS = ('ralph02.te2',)

def PIP_INSTALL(env):
    if env.host.endswith('.te2'):
        return 'pip install --proxy=repo.dc2:8000 -e .'
    return 'pip install -e .'
