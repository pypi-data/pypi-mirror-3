#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012 Ciaran Farrell <cfarrell1980@gmail.com>
# This file is part of the termine package. You can find the
# source (python) of termine at http://bitbucket.org/cfarrell1980/termine/
# This file (and the rest of termine) is licensed under the MIT license. You
# can find the text of this license in the LICENSE.txt file distributed with
# termine. Alternatively, you can read the license online in the bitbucket
# repository at the following URL:
# https://bitbucket.org/cfarrell1980/termine/raw/ddf534649df6/LICENSE.txt
from termine.gwise import Groupwise,CONFIGFILE,initialConfig
from termine.gwexceptions import *
import ConfigParser,os
try:
  import argparse
except ImportError:
  raise GWFatalException, 'For Python < 2.7 you need to install argparse'
  

config = ConfigParser.SafeConfigParser()
if not os.path.isfile(CONFIGFILE):
  initialConfig(CONFIGFILE)
config.read(CONFIGFILE)
DEFAULT_FMT = config.get('Global','DEFAULT_FMT')
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--verbose', '-v', action='count')
parser.add_argument('--version', action='version', version='%(prog)s 1')
parser.add_argument('--format','-f', dest='format', default=DEFAULT_FMT)
parser.add_argument('--force-login', dest='forcelogin', action="store_true",
                    default=False)
