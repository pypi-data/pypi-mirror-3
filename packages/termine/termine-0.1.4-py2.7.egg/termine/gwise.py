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
from hashlib import sha256
from datetime import datetime
from termine.genericlogger import logger
from getpass import getpass,getuser
from datetime import timedelta,datetime
from termine.filters import GWFilter
from termine.gwexceptions import *
from random import  sample
from ConfigParser import NoOptionError
from string import digits, ascii_letters
from time import sleep
import sys,os,json,logging,ConfigParser,base64,pkgutil,tempfile
try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError,"Please install python-suds"

# sometimes the suds client blows up if there is a soap error and there is
# no logger configured
logging.getLogger('suds.client').setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

# check if there is a .termine directory in /tmp
TMPDIR = os.path.join(os.path.expanduser('~/.termine/'))
if not os.path.isdir(TMPDIR):
  logger.debug('No temporary directory %s'%TMPDIR)
  try:
    os.mkdir(TMPDIR)
  except Exception,e:
    raise gwFatalException, 'Failed to created %s: %s'%(TMPDIR,str(e))
else:
  logger.debug('Temporary directory %s exists'%TMPDIR)
# now check if the required files are in TMPDIR
req = ['groupwise.wsdl','types.xsd','methods.xsd','archive.xsd',
        'events.xsd','archive.wsdl']
for f in req:
  uri = os.path.join(TMPDIR,f)
  if not os.path.isfile(uri):
    logger.debug('%s was not found - creating it now...'%uri)
    try:
      content = pkgutil.get_data('termine','../data/%s'%f)
      fd = open(uri,'wb')
      fd.write(content)
      fd.close()
    except Exception,e:
      raise GWFatalException,'Failed to create %s: %s'%(uri,str(e))
    else:
      logger.debug('Successfully created %s'%uri)

CONFIGFILE = os.path.expanduser('~/.gwise.cfg')
CACHEFILE = os.path.expanduser('~/.gwise-id.cache')
THISDIR = os.path.abspath(sys.argv[0])# /usr/bin/ - where termine installed

def initialConfig(cfg):
  ''' Write the default configuration to CONFIGFILE and then
      change the permissions on that file to ensure it is only
      readable by the user. This is because the file will contain
      a session cookie from Groupwise '''
  uname=raw_input('Username [%s]: ' % getuser())
  if (uname == ''):
    uname = getuser()
  wsdl = 'file://%s'%os.path.join(TMPDIR,'groupwise.wsdl')
  gway = raw_input('Gateway: ')
  config = ConfigParser.RawConfigParser()
  config.add_section('Global')
  config.set('Global','wsdl', '%s'%wsdl)
  config.set('Global','gateway',  '%s'%gway)
  config.set('Global','lang', 'en')
  config.set('Global','app', 'PyGw')
  config.set('Global','version', '0.1')
  config.set('Global','userid', '1000')
  config.set('Global','system', '1')
  config.set('Global','session', '')
  config.set('Global','window', 'today')
  config.set('Global','datetime','%Y-%m-%d %H:%M')
  config.set('Global','start_date_fmt','%a %d/%m %H:%M')
  config.set('Global','end_date_fmt','%H:%M')
  config.set('Global','uname', uname)
  config.set('Global','attempts','0')
  config.set('Global','DEFAULT_FMT','raw')
  config.set('Global','defaultwindow','thisweek')
  config.set('Global','coloring','True')
  config.set('Global','defaultdomain','suse.com')
  config.set('Global','cachetimeoutdays','300')
  fd = open(cfg,'w')
  config.write(fd)
  fd.close()
  os.chmod(cfg,0600)


class Groupwise:
  def __init__(self,fl=False):
    ''' Initialise by reading the configuration. Immediately try to connect to
        the Groupwise server to retrieve a list of categories. This is done to
        check if the user is authenticated. If the session cookie works without
        problem, we are obviously using a valid cookie and do not need to login
    '''
    self.cfg = CONFIGFILE
    if not os.path.isfile(self.cfg):
      logger.warn('no config file found at %s - generating one now'%self.cfg)
      initialConfig(self.cfg)
    self.threshold_attempts = 2 # you will be locked out of server!
    self.config = ConfigParser.SafeConfigParser()
    self.config.read(self.cfg)
    try:
      self.wsdl = self.config.get('Global','wsdl')
    except NoOptionError,e:
      raise GWFatalException, 'Your config file does not have a WSDL entry'
    else:
      if self.wsdl == '':
        raise GWFatalException, 'Your config file WSDL entry is empty'
    try:
      self.gateway = self.config.get('Global','gateway')
    except NoOptionError,e:
      raise GWFatalException, 'Your config file does not have a gateway entry'
    else:
      if self.gateway == '':
        raise GWFatalException, 'Your config file gateway entry is empty'
    self.lang = self.config.get('Global','lang')
    self.app = self.config.get('Global','app')
    self.version = self.config.get('Global','version')
    self.userid = self.config.getint('Global','userid')
    self.system = self.config.getint('Global','system')
    self.dtime = self.config.get('Global','datetime',raw=True)
    self.session = self.config.get('Global','session',raw=True)
    self.defaultwindow=self.config.get('Global','window')
    self.uname = self.config.get('Global','uname')
    self.defaultdomain = self.config.get('Global','defaultdomain')
    self.client,self.pt = None,None
    self.gwVersion = None
    self.build = None
    self.serverUTCTime = None
    self.uuid = None
    self.name= None
    self.addressbookid = None
    try:
      logger.debug('creating Client using wsdl=%s'%self.wsdl)
      self.client = Client(self.wsdl)
      cache = self.client.options.cache
      logger.debug('Setting suds client cache to 300 days')
      cache.setduration(days=300)
      self.client.set_options(cache=cache)
      self.client.set_options(port='GroupwiseSOAPPort')
      logger.debug('setting client option gateway=%s'%self.gateway)
      self.client.set_options(location=self.gateway)
      self.pt = self.client.factory.create('ns2:PlainText')
    except TransportError,e:
      raise GWFatalException, 'Check your WSDL file and Gateway URLs!'
    except Exception,e:
      logger.debug(str(e))
      raise GWFatalException,str(e)
    else:

      self.pt.username = self.uname
      if fl:
        self.__login__()
        raise GWForceLoginException,'User forced login - complying...'
      if self.session == '':
        self.__login__()
        raise GWSessionException,'no session cookie - retrying...'
      logger.info('setting soapheaders to "%s"'%self.session)
      self.client.set_options(soapheaders=self.session)
      # TODO: get the calendar lookup out of init. all we need is some 
      # method that requires authentication to test existing session or
      # to force authentication prompt
      try:
        self.addressbookid = self.getContactFolderId()
      except GWLoginException,e:
        logger.warn('session login failed: %s'%str(e))
        self.__login__()
        raise GWInitException, 'session login failed - retrying...'
      except GWSessionException,e:
        logger.warn('session login failed: %s'%str(e))
        self.__login__()
        raise GWInitException, 'session login failed - retrying...'
      except GWFatalException:
        raise
      except Exception,e:
        logger.error(str(e))
        raise GWFatalException, 'Cannot continue: %s'%str(e)
      else:
        logger.debug('successfully picked up category listings as test for auth')
      

  def __incrementAttempts__(self,newinc):
    ''' If the user enters the wrong password too often the Groupwise server
        can block him and he will have to contact sysadmin to get his account
        unblocked. Try to warn the user by keeping count of how many times the
        wrong password was entered. As Groupwise keeps count itself, we need to
        keep count across e.g. multiple terminals' - which is why we use a 
        persistent storage like the config file '''
    fd = open(self.cfg,'w')
    self.config.set('Global','attempts',str(newinc))
    self.config.write(fd)
    fd.close()

  def __resetAttempts__(self):
    ''' Reset the count of wrong passwords to 0. Typically, this is done when
        login was successful '''
    fd = open(self.cfg,'w')
    self.config.set('Global','attempts',str(0))
    self.config.write(fd)
    fd.close()

  def __setUser__(self,user):
    ''' Once a user successfully logs in, write the username used to the config
        file so it will be automatically offered as default the next time '''
    fd = open(self.cfg,'w')
    self.config.set('Global','uname',user)
    self.config.write(fd)
    self.uname = user # just in case?
    fd.close()

  def __login__(self):
    ''' The main login routine. Note that this method keeps retrying by asking
        the user for password '''
    invalid=True
    while invalid:
      self.pt.username = self.uname
      self.pt.password = getpass(self.pt.username + ' Groupwise password: ')
      resp = self.client.service.loginRequest(self.pt,self.lang,
        self.app,self.userid,self.system)
      if int(resp.status.code)==0:
        logger.info('Password ok. Creating and storing session details')
        invalid=False
      else:
        attempts = self.config.getint('Global','attempts')
        self.__incrementAttempts__(attempts+1)
        attempts = self.config.getint('Global','attempts')
        if int(resp.status.code)==55061: # too many login attempts
          raise GWFatalException, 'Too many login attempts (recently). Login temporarily disabled'
        if attempts >= self.threshold_attempts:
          logger.warn('%d login attempts! Careful - your account will be disabled and you will have to contact sysadmin!'%attempts)
    self.__resetAttempts__()
    self.session = resp.session
    self.config.set('Global','session',self.session)
    self.config.write(open(self.cfg,'w'))
    self.name = resp.userinfo.name
    self.build = resp.build
    self.gwVersion = resp.gwVersion
    self.uuid = resp.userinfo.uuid
    self.serverUTCTime = resp.serverUTCTime
    utcnow = datetime.utcnow()
    if utcnow.hour != self.serverUTCTime.hour:
      logger.warn("Warning: server UTC is %s and local UTC is %s"%(self.serverUTCTime.strftime(self.dtime),
        utcnow.strftime(self.dtime)))
        
  def getContactFolderId(self):
    '''Retrieves the id of the users contact folder'''
    logger.debug('Groupwise.getContactFolderId')
    try:
      resp = self.client.service.getFolderRequest(folderType='Contacts')
    except Exception,e:
      raise GWFatalException, 'getFolderRequest failed for Contacts'
    else:
      if int(resp.status.code)==0:
        if hasattr(resp.folder,'id'):
          return resp.folder.id
        else:
          raise GWItemFetchException,'Could not retrieve Address Book id'
      else:
        raise GWFatalException,resp.status.description

  def getAppointments(self,window=None):
    ''' Retrieves the user appointments by acting as a wrapper around the
        getCalendarItems method. Can optionally use a filter such as
        today, tomorrow, thisweek - to narrow down the appointments. By default
        the filter is today '''
    logger.debug('Groupwise.getAppointments')
    if not window: window = self.defaultwindow
    gwfilter = GWFilter(self.client)
    windowmap = { 'today':gwfilter.today,
                    'tomorrow':gwfilter.tomorrow,
                    'thisweek':gwfilter.thisweek,
                    'yesterday':gwfilter.yesterday,
                    'thismonth':gwfilter.thismonth,
                    'thisyear':gwfilter.thisyear,
                  }
    if window.lower() not in windowmap.keys():
      # check if window.lower() can fit our strptime pattern
      try:
        specific_date = datetime.strptime('%Y-%m-%d',window.lower())
      except ValueError:
        logger.warn("%s not recognized. Using default (%s)"%(window,
            self.defaultwindow))
      else:
        logger.info('%s parsed to %Y-%m-%d. Calling specificdate filter'%window.lower())
        try:
          items = self.getCalendarItems(gwfilter.specificdate(specific_date))
        except GWLoginException,e:
          logger.warn('session login failed: %s'%str(e))
          self.__login__()
          raise GWInitException, 'session login failed - retrying...'
        except GWSessionException,e:
          logger.warn('session login failed: %s'%str(e))
          self.__login__()
          raise GWInitException, 'session login failed - retrying...'
        except GWFatalException:
          raise
        except Exception,e:
          logger.error(str(e))
          raise GWFatalException, 'Cannot continue: %s'%str(e)
        else:
          return items
    else:
      try:
        items = self.getCalendarItems(windowmap.get(window,
          windowmap[self.defaultwindow])())
      except GWLoginException,e:
        logger.warn('session login failed: %s'%str(e))
        self.__login__()
        raise GWInitException, 'session login failed - retrying...'
      except GWSessionException,e:
        logger.warn('session login failed: %s'%str(e))
        self.__login__()
        raise GWInitException, 'session login failed - retrying...'
      except GWFatalException:
        raise
      except Exception,e:
        logger.error(str(e))
        raise GWFatalException, 'Cannot continue: %s'%str(e)
      else:
        return items

    
  def getCalendarItems(self,filtergroup):
    ''' Responsible for actually using the Groupwise SOAP API to return
        the filtered list of user appointments '''
    logger.debug('Groupwise.getCalendarItems')
    resp = self.client.service.getFolderRequest(folderType='Calendar')
    if int(resp.status.code)==53273: # "Invalid Password"
      logger.warn('invalid password (or none provided)')
      raise GWLoginException(resp.status.description)
    if int(resp.status.code)==59920: # "missing session string"
      logger.warn("missing session string")
      raise GWSessionException(resp.status.description)
    if int(resp.status.code)==59910: # invalid session string
      logger.warn("invalid session string")
      raise GWSessionException(resp.status.description)
    Filter = self.client.factory.create('ns2:Filter')
    Filter.element = filtergroup
    items = self.client.service.getItemsRequest(resp.folder.id,
      "default",Filter,None)
    return items


  def getCategoryListRequest(self):
    ''' Used to test if the session cookie is valid. Chosen because it looks 
        like one of the only methods in the Groupwise API with a fast
        response time '''
    items = self.client.service.getCategoryListRequest()
    return items


  def getItemRequest(self,itemid):
    ''' Retrieve an item with id=itemid from Groupwise. Generally, this is
        used to return a particular Groupwise appointment. Note that the
        message is not included as part of default view (Groupwise considers
        the message of the appointment to be an attachment). Thus, we need
        to add message to the default'''
    item = self.client.service.getItemRequest(itemid,'default message')
    if int(item.status.code) == 59906:
      raise GWItemFetchException,'No appointment with that id found'
    if int(item.status.code) == 53511:
      raise GWItemFetchException, 'Either no such appointment or you do not have permission to view it'
    if int(item.status.code) != 0:
      msg = 'Groupwise said "%s" - are you sure %s is a real short URI from termine -l?'%(item.status.description,itemid)
      raise GWItemFetchException, msg
    return item

  def getBusyTimeRequestId(self,users):
    logger.debug('Groupwise.getBusyTimeRequestId with %s'%users)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    delta = timedelta(days=7)
    s = datetime.utcnow()
    e = s+delta
    s_str,e_str = s.strftime(fmt),e.strftime(fmt)
    free_busy_list = self.client.factory.create('ns2:FreeBusyUserList')
    for u in users.keys():
      n_and_e = self.client.factory.create('ns2:NameAndEmail')
      n_and_e.uuid = users[u]['uuid']
      n_and_e.email = users[u]['email']
      n_and_e.displayName = users[u]['displayName']
      free_busy_list.user.append(n_and_e)
    resp = self.client.service.startFreeBusySessionRequest(users=free_busy_list,
      startDate=s_str,endDate=e_str)
    if int(resp.status.code)==0:
      return int(resp.freeBusySessionId)
    else:
      raise GWFatalException,resp.status.description

  def __parseBusyBlocks__(self,udict):
    '''Use Dyck-Words type algorithm to find out what the available times
       are'''
    logger.debug('Groupwise.__parseBusyBlocks__()')
    dtlist = []
    free = []
    for k in udict.keys():
      blocks = udict[k]['blocks'].block
      
      for block in blocks:
        dtlist.append((block.startDate,0))
        dtlist.append((block.endDate,1))
    dtlist.sort()
    #print dtlist
    i = 0
    dyck = 0
    previous = 0 # need to check for a rising or falling edge
    for stamp in dtlist:
      previous = dyck
      if stamp[1] == 0: # startDate
        dyck += 1
      else:
        dyck -= 1
      if i == 0:
        if (dyck==1) and (previous==0):
          free.append([None,stamp[0]])
        elif dyck == 0:
          free.append([stamp[0]])
      else:
        if dyck == 0:
          free.append([stamp[0]])
        else:
          if (dyck == 1) and (previous == 0): # rising
            free[-1].append(stamp[0])
      i+=1
    print free
    #print udict
    return udict

  def getBusyTimes(self,sessionid):
    logger.debug('Groupwise.getBusyTimes with id %s'%sessionid)
    finished = False
    tlimit = timedelta(seconds=30)# should probably go in config
    s = datetime.now()
    e = s+tlimit
    u = {}
    while not finished:# loop is needed as server might not be ready 1st time
      resp = self.client.service.getFreeBusyRequest(sessionid)
      if int(resp.status.code)==0:
        outstanding = int(resp.freeBusyStats.outstanding)
        #TODO: rather than the 'or' in the next line check each condition
        #individually. That way the warning can be that the threshold time for
        #getting responses from GW has been exceeded
        users = resp.freeBusyInfo.user
        for user in users:
          u[user.email] = {'email':user.email,'uuid':user.uuid,
                          'displayName':user.displayName,
                          'blocks':user.blocks}
        if (outstanding == 0) or (datetime.now() >= e):
          self.client.service.closeFreeBusySessionRequest(sessionid)
          logger.debug('GW server says he is finished. Get out of here')
          return self.__parseBusyBlocks__(u)
          finished = True
        
      if datetime.now() >= e:
        return self.__parseBusyBlocks__(u)
        finished = True
      logger.debug('sleeping for 2 seconds before asking GW server again')
      sleep(2) # don't hammer the GW server too often
    return self.__parseBusyBlocks__(u)
    
  def getUserList(self,users):
    logger.debug('Groupwise.getUserList with %s'%users)
    FilterGroup = self.client.factory.create('ns2:FilterGroup')
    FilterGroup.op = 'or'
    u = {}
    for user in users:
      user1 = user.split('@')[0]
      u[user1] = {'uuid':None}
      FilterEntry = self.client.factory.create('ns2:FilterEntry')
      FilterEntry.field = 'username'
      FilterEntry.value = user
      logger.debug('FilterEntry created with field username = %s'%user)
      FilterEntry.op = 'eq'
      FilterGroup.element.append(FilterEntry)
    Filter = self.client.factory.create('ns2:Filter')
    Filter.element = FilterGroup
    resp = self.client.service.getItemsRequest(self.addressbookid,
        None,Filter,None)
    if int(resp.status.code)==0:
      if len(resp.items)==0:
        return {}
      items = resp.items[0]
      for item in items:
        if hasattr(item,'uuid'):
          email = item.emailList._primary
          uname = item.emailList._primary.split('@')[0].lower()
          displayName = item.fullName.displayName
          uuid = item.uuid
          if u.has_key(uname):
            u[uname]['email'] = email
            u[uname]['uuid'] = uuid
            u[uname]['displayName'] = displayName
          else:
            logger.warn('%s was found on the Groupwise server but was not requested'%uname)
        else:
          logger.warn('No uuid known for user with id %s'%item.id)
      return u
    else:
      raise GWFatalException,'Get me out of here!'


class GWIdCache:
  def __init__(self):
    if not os.path.isfile(CACHEFILE):
      logger.info('%s not found - creating empty file with correct permissions now'%CACHEFILE)
      self.__initCache__(CACHEFILE)

  def __initCache__(self,cachefile):
    logger.debug('initCache with cachefile %s'%cachefile)
    fd = open(cachefile,'w')
    json.dump({},fd)
    fd.close()
    os.chmod(cachefile,0600)

  def shorten(self,url,length=5):
    logger.debug('GWIdCache.shorten(url=%s,length=%s)'%(url,length))
    x = "".join(sample(digits + ascii_letters, length))
    fd = open(CACHEFILE,'r')
    j = json.load(fd)
    j1 = dict((v, k) for k, v in j.items())
    if j1.has_key(url):
      logger.debug('Found %s in cache'%url)
      fd.close()
      return j1[url]
    while j.has_key(x):
      logger.debug('cache file already knows short %s - regenerating'%x)
      x= "".join(sample(digits + ascii_letters, length))
    j[x] = url
    logger.debug('shortened %s to %s'%(url,x))
    fd.close()
    fd = open(CACHEFILE,'w')
    json.dump(j,fd)
    fd.close()
    return x
    
  def expand(self,short):
    logger.debug('GWIdCache.expand(%s)'%short)
    fd = open(CACHEFILE,'r')
    j = json.load(fd)
    fd.close()
    if not j.has_key(short):
      logger.warn('short key %s could not be expanded!'%short)
      raise KeyError, 'short key %s could not be expanded'%short
    else:
      return j[short]
    
      


if __name__ == '__main__':
  sys.stdout.write('Refactored functionality to termine. Use that script now\n')
  sys.exit(0)


