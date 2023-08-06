# -*- coding: utf-8 -*-
# Copyright (c) 2012 Ciaran Farrell <cfarrell1980@gmail.com>
# This file is part of the termine package. You can find the
# source (python) of termine at http://bitbucket.org/cfarrell1980/termine/
# This file (and the rest of termine) is licensed under the MIT license. You
# can find the text of this license in the LICENSE.txt file distributed with
# termine. Alternatively, you can read the license online in the bitbucket
# repository at the following URL:
# https://bitbucket.org/cfarrell1980/termine/raw/ddf534649df6/LICENSE.txt
import logging,sys
logger = logging.getLogger('gwiseLogger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler( sys.__stdout__ ) # Add this
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
