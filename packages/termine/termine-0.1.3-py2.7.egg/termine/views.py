#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gwise import Groupwise, CONFIGFILE, initialConfig,GWIdCache
from genericlogger import logger
from datetime import timedelta,datetime
from time import timezone,strftime,gmtime
import os,json,ConfigParser,sys,base64,textwrap
try:
  import curses
except ImportError:
  logger.warn('You should install python-curses')
utcoffset = timezone / -(60*60)
delta = timedelta(hours=utcoffset)
config = ConfigParser.SafeConfigParser()
if not os.path.isfile(CONFIGFILE):
  initialConfig(CONFIGFILE)
config.read(CONFIGFILE)
try:
  dtime = config.get('Global','start_date_fmt',raw=True)
  etime = config.get('Global','end_date_fmt',raw=True)
  coloring = config.getboolean('Global','coloring')
except NoOptionError,e:
  raise GWConfigFileException, 'You should remove %s and re-run the script'%CONFIGFILE

cache = GWIdCache()

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


class GWView:

  def __init__(self,soapstring,id=False,fullid=False):
    logger.debug('GWView.__init__')
    logger.debug('utcoffset is %s [%s] (%s)'%( utcoffset,type(utcoffset),
                                      strftime("%Z", gmtime())))
    self.has_colours = self.__hasColours__(sys.stdout)
    self.itemlist = self.__soap2json__(soapstring)
    self.id = id # whether to show the id or not
    self.fullid = fullid # whether to show the full id string

  #following from Python cookbook, #475186
  def __hasColours__(self,stream):
    ''' Simply checks if the terminal being used has the capability of 
        displaying colours '''
    if not coloring: return False # if the config file says no coloring
    if not hasattr(stream, "isatty"):
      return False
    if not stream.isatty():
      return False # auto color only on TTYs
    try:
      curses.setupterm()
      return curses.tigetnum("colors") > 2
    except ImportError:
      logger.info('install python-curses for color')	
    except Exception,e:
      logger.warn('curses is present but could not be imported: %s'%str(e))
      return False

  def __colorize__(self,text, colour=WHITE,bold=False):
    ''' Prefix and append the appropriate ANSI color codes to text to
        make the text display in colour on the colour-enabled terminal '''
    if self.has_colours:
      prefix = ""
      logger.debug('have color capability. Colorizing ...')
      if bold:
        prefix = "\033[1m"
      seq = "%s\x1b[1;%dm" % (prefix,(30+colour)) + text + "\x1b[0m"
      return seq
    else:
      logger.debug('no color capabilities detected for this tty')
      return text

  def __appointmentStatus__(self,s,f):
    '''Return integer to show chronological status of appointment
       @s datetime representing start of appointment
       @f datetime representing finish of appointment
       @returns MAGENTA (appointment is over)
                GREEN (appointment in future)
                RED (appoinment currently taking place)'''
    current_localtime = datetime.now()
    # appointment is over
    if f < current_localtime:
      return MAGENTA
    # appointment in the future
    elif s > current_localtime:
      return BLUE
    # appointment is currently taking place
    elif ((s < current_localtime) and (f > current_localtime)):
      return RED

  def __readableId__(self,gwid):
    ''' The id that Groupwise sends is a long string with many dots. If we
        split the string on the dots we see that only two list entries are
        distinct (0 and 6). Hence, it is (theoretically) possible to shorten
        the id displayed to the user. If the user choose --with-fullid then we
        simply return the string without doing anything '''
    logger.debug('__readableId__(gwid=%s)'%gwid)
    if self.fullid:
      logger.debug('self.fullid is True')
      return gwid
    else:
      logger.debug('self.fullid is False')
      logger.debug('shortening %s'%gwid)
      return cache.shorten(gwid)
    

  def __soap2json__(self,soapstring):
    ''' Parse the SOAP object sent back by the Groupwise API and create a 
        dictionary out of it which can be used directly by this class - or
        which can be converted to JSON (need to format datetime as string for
        JSON conversion though)'''
    l = []
    logger.debug('GWView.__soap2json__')
    if not hasattr(soapstring.items,'item'):
      return l
    itemslist = soapstring.items.item
    for item in itemslist:
      t = {'hasAttachment':False,'timezone':None}
      t['size'] = item.size
      t['acceptLevel'] = item.acceptLevel
      t['created'] = item.created
      t['delivered'] = item.delivered
      t['startDate'] = item.startDate
      t['endDate'] = item.endDate
      if hasattr(item,'hasAttachment'):
        t['hasAttachment'] = item.hasAttachment
      t['iCalId'] = item.iCalId
      t['id'] = item.id
      t['modified'] = item.modified
      t['msgId'] = item.msgId
      t['priority'] = item.options.priority
      if hasattr(item,'status'):
        if hasattr(item.status,'accepted'):
          t['accepted'] = item.status.accepted
        if hasattr(item.status,'delegated'):
          t['delegated'] = item.status.delegated
        if hasattr(item.status,'opened'):
          t['opened'] = item.status.opened
        if hasattr(item.status,'read'):
          t['read'] = item.status.read
      t['subject'] = item.subject
      if hasattr(item,'timezone'):
        logger.debug('this item has a timezone component but we do not handle it yet')
        #t['timezone'] = item.timezone
      t['version'] = item.version
      l.append(t)
    return l

  def render(self):
    ''' This is the default render method used if format=raw is requested.
        Currently format=raw is the default. This method checks the status of
        the appointment (over, running, future) using the __appointmentStatus__
        method and the output is colour coded accordingly (if the terminal
        supports colour coding)'''
    logger.debug('GWView.render')
    if not len(self.itemlist):
      print self.__colorize__("No appointments. Yay!",GREEN)
    for item in self.itemlist:
      buggy = (item['startDate']+delta)
      buggy1 = (item['endDate']+delta)
      subject = item['subject'].encode('utf-8')
      status = self.__appointmentStatus__(buggy,buggy1)
      buggy = buggy.strftime(dtime)
      buggy1 = buggy1.strftime(etime)
      with_id = ""
      if self.id: with_id = "%s\t"%self.__readableId__(item['id']).encode('utf-8')
      msg = "%s - %s\t%s%s"%(buggy,buggy1, with_id, subject)
      print self.__colorize__(msg,status)

class GWJSONView(GWView):
  '''This class is derived from the base GWView class. It just overrides the
     render method to return JSON encoded output '''
  def render(self):
    return json.dumps(self.itemlist)


class GWHTMLView(GWView):
  def render(self):
    logger.debug('GWHTMLView.render')
    return self.itemlist

"""
'acceptLevel', 'alarm', 'allDayEvent', 'container', 'created', 'delivered', 'distribution', 'endDate', 'iCalId', 'id', 'message', 'modified', 'msgId', 'options', 'place', 'security', 'size', 'source', 'startDate', 'status', 'subject', 'timezone', 'version'
"""
class GWAppointmentView:
  def __init__(self,soapobj):
    self.d = self.__soap2string__(soapobj)

  def __soap2string__(self,soapobj):
    item = soapobj.item
    t = {'message':'This appointment does not contain a message/description',
          'place': 'This appointment does not contain a place'}
    t['acceptLevel'] = item.acceptLevel
    if hasattr(item,'alarm'):
      if hasattr(item.alarm,'_enabled'):
        t['alarmEnabled'] = item.alarm._enabled
      if hasattr(item.alarm,'value'):
        t['alarmValue'] = int(item.alarm.value)
    t['size'] = int(item.size)
    if hasattr(item,'allDayEvent'):
      t['allDayEvent'] = item.allDayEvent
    t['startDate'] = item.startDate
    t['endDate'] = item.endDate
    t['id'] = item.id
    t['iCalId'] = item.iCalId
    t['modified'] = item.modified
    if hasattr(item,'place'):
      t['place'] = item.place
    if hasattr(item,'status'):
      if hasattr(item.status,'accepted'):
        t['accepted'] = item.status.accepted
      if hasattr(item.status,'delegated'):
        t['delegated'] = item.status.delegated
      if hasattr(item.status,'opened'):
        t['opened'] = item.status.opened
      if hasattr(item.status,'read'):
        t['read'] = item.status.read
    t['version'] = item.version
    t['source'] = item.source
    t['subject'] = item.subject
    if hasattr(item,'timezone'):
      logger.debug('this item has a timezone component but we do not handle it yet')
      #t['timezone'] = item.timezone
    if hasattr(item,'message'):
      if hasattr(item.message,'part'):
        if len(item.message.part):
          if hasattr(item.message.part[0],'value'):
            t['message'] = base64.b64decode(item.message.part[0].value)
    return t
    
  def bold(self,text):
    p,s = "\033[1m","\033[0m"
    return '%s%s%s'%(p,text,s)

  def render(self):
    s = textwrap.dedent(self.d['subject'].encode('utf-8'))
    p = textwrap.dedent(self.d['place'].encode('utf-8'))
    m = textwrap.dedent(self.d['message'].decode('utf-8'))

    print "%s %s"%(self.bold('Subject:'),textwrap.fill(s,initial_indent='', subsequent_indent=' '*9))
    print self.bold("From:")+"    %s"%textwrap.fill("%s - %s"%(self.d['startDate'].strftime(dtime),self.d['endDate'].strftime(dtime))
        , initial_indent='', subsequent_indent=' '*9)
    print self.bold('Place:')+"   %s"%textwrap.fill(p, initial_indent='', subsequent_indent=' '*9)
    print self.bold('Message:')+" %s"%textwrap.fill(m.encode('utf-8'), initial_indent='', subsequent_indent=' '*9)


class GWSimpleBusyView:
  def __init__(self,udict):
    logger.debug('GWSimpleBusyView.__init__()')
    self.udict = udict

  def render(self):
    logger.debug('GWSimpleBusyView.render()')
    #print self.udict
