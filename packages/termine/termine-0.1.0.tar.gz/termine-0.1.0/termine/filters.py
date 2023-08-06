# Copyright (c) 2012 Ciaran Farrell <cfarrell1980@gmail.com>
# This file is part of the termine package. You can find the
# source (python) of termine at http://bitbucket.org/cfarrell1980/termine/
# This file (and the rest of termine) is licensed under the MIT license. You
# can find the text of this license in the LICENSE.txt file distributed with
# termine. Alternatively, you can read the license online in the bitbucket
# repository at the following URL:
# https://bitbucket.org/cfarrell1980/termine/raw/ddf534649df6/LICENSE.txt
from termine.genericlogger import logger
from datetime import datetime
class GWFilter:
  def __init__(self,client):
    logger.debug('initializing GWFilter')
    self.dtfmt = "%Y-%m-%dT%H:%M:%SZ"
    self.start_str = "%Y-%m-%dT00:00:00Z"
    self.end_str =   "%Y-%m-%dT23:59:59Z"
    self.FilterGroup = client.factory.create('ns2:FilterGroup')
    self.FilterGroup.op = 'and'
    self.Appointment = client.factory.create('ns2:FilterEntry')
    self.Appointment.field = '@type'
    self.Appointment.value = 'Appointment'
    self.Appointment.op = 'eq'
    self.Start = client.factory.create('ns2:FilterEntry')
    self.x = client.factory.create('ns2:FilterDate')
    self.End = client.factory.create('ns2:FilterEntry')
    self.y = client.factory.create('ns2:FilterDate')
    
  def specificDate(self,dt):
    ''' Find all appointments on a specific date. These are the
        appointments that start on or before the date and end on
        or after the specific date. This way we also capture e.g. 
        appointments that span an entire week and include the specific
        date '''
    logger.debug('GWFilter.specificDate(%s)'%dt)
    s = datetime.strptime(dt.strftime(self.start_str),self.dtfmt)
    e = datetime.strptime(dt.strftime(self.end_str),self.dtfmt)
    self.Start.field = 'startDate'
    self.Start.op = 'fieldLTE'
    self.Start.date = s.strftime(self.dtfmt)
    self.End.field = 'endDate'
    self.End.op = 'fieldGTE'
    self.End.date = e.strftime(self.dtfmt)
    #self.End.value = None
    self.FilterGroup.element.append(self.Appointment)
    self.FilterGroup.element.append(self.Start)
    self.FilterGroup.element.append(self.End)
    print self.FilterGroup
    return self.FilterGroup

  def today(self):
    logger.debug('GWFilter.today()')
    self.Start.field = 'startDate'
    self.Start.op = 'fieldLTE'
    self.Start.date = self.x.Today
    #self.Start.value = -1
    self.End.field = 'endDate'
    self.End.op = 'fieldGTE'
    self.End.date = self.x.Today
    #self.End.value = 1
    self.FilterGroup.element.append(self.Appointment)
    self.FilterGroup.element.append(self.Start)
    self.FilterGroup.element.append(self.End)
    return self.FilterGroup

  def tomorrow(self):
    logger.debug('GWFilter.tomorrow()')
    self.Start.field = 'startDate'
    self.Start.op = 'fieldLTE'
    self.Start.date = self.x.Tomorrow
    self.End.field = 'endDate'
    self.End.op = 'fieldGTE'
    self.End.date = self.x.Tomorrow
    self.FilterGroup.element.append(self.Appointment)
    self.FilterGroup.element.append(self.Start)
    self.FilterGroup.element.append(self.End)
    return self.FilterGroup

  def thisweek(self):
    logger.debug('GWFilter.thisweek()')
    self.Start.field = 'startDate'
    self.Start.op = 'fieldLTE'
    self.Start.date = self.x.ThisWeek
    self.End.field = 'endDate'
    self.End.op = 'fieldGTE'
    self.End.date = self.x.ThisWeek
    self.FilterGroup.element.append(self.Appointment)
    self.FilterGroup.element.append(self.Start)
    self.FilterGroup.element.append(self.End)
    return self.FilterGroup
