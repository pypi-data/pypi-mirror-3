# Copyright (c) 2012 Ciaran Farrell <cfarrell1980@gmail.com>
# This file is part of the termine package. You can find the
# source (python) of termine at http://bitbucket.org/cfarrell1980/termine/
# This file (and the rest of termine) is licensed under the MIT license. You
# can find the text of this license in the LICENSE.txt file distributed with
# termine. Alternatively, you can read the license online in the bitbucket
# repository at the following URL:
# https://bitbucket.org/cfarrell1980/termine/raw/ddf534649df6/LICENSE.txt
class GWLoginException(BaseException):
  pass

class GWSessionException(BaseException):
  pass

class GWInitException(BaseException):
  pass

class GWConfigFileException(BaseException):
  pass

class GWFatalException(BaseException):
  pass

class GWItemFetchException(BaseException):
  pass

class GWForceLoginException(BaseException):
  pass
