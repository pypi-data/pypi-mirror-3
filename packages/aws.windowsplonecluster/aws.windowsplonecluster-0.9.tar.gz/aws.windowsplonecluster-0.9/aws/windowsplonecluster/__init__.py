# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Copyright (C) 2011 Alterway Solutions 

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation,
# 51 Franklin Street, Suite 500, Boston, MA 02110-1335,USA

import os
import sys
import shutil
import re
import socket
import logging
import logging.handlers
import datetime
import urllib
import time
import tempfile
import subprocess
import threading
import Queue

from time import sleep
from ConfigParser import ConfigParser
from optparse import OptionParser
from utils import rlines
from inspect import getmodule
from zope import interface
from zope import component


try:
    from win32com.client import GetObject
    from win32serviceutil import StopService
    from win32serviceutil import StartService
    from win32serviceutil import RestartService
    from win32serviceutil import QueryServiceStatus
    from wmi import WMI
except ImportError:

    def StopService(serviceName, machine = None):
        return (16, 1, 0, 0, 0, 0, 0)

    def StartService(serviceName, args = None, machine = None):
        return

    def RestartService(serviceName, args = None, waitSeconds = 30,
                       machine = None):
        return

    def QueryServiceStatus(serviceName, machine=None):
        ## 1 - service is stop
        ## 4 - service is start
        ## 3 - service is stopping
        return (16, 1, 0, 0, 0, 0, 0)

    def getObject(name):
        return

    class WMI(object):
        
        def Win32_Process(self, machine = None):
            return ()

import interfaces

logger = logging.getLogger('ctl')
logperf = logging.getLogger('ctl.perf')
BACKEND = re.compile("#*BackEnd[^E]*#*End", re.M)
BLANK_LINE = re.compile(r"^\s+\n$", re.M)
BASE = 'VirtualHostBase/http/%s:80/%s/VirtualHostRoot'
URL = 'http://%s:%s@%s:%s/%s/%s'
DIRECT_URL = 'http://%s:%s@%s:%s/%s'
STOP_SEARCH = 'Zope Ready to handle requests'
wmi = dict()
gsm = component.getGlobalSiteManager()

def isRunning(pid):
    wmi = GetObject('winmgmts:')
    if wmi is not None:
        processes = wmi.InstancesOf('Win32_Process')
        f = [x for x in processes if x.ProcessId == int(pid)]
        return len(f) > 0


def clear(func):
    """ decorator that clear the status check """
    
    def clear(self,*args,  **kwargs):
        if hasattr(self, 'clear'):
            self.clear()
        return func(self, *args, **kwargs)

    return clear

def no_raise(func):
    """ decorator that avoid an exepction but send an mail """
    
    def wrap(*arg, **args):
        try:
            return func(*arg, **args)
        except:
            logger.critical("There is an exception when calling "
                            "the function %s with args %s %s" % (func.__name__,
                                                              str(*arg),
                                                              str(**args)))
            logger.exception(func.__name__)
    return wrap


def ifIsDeadDoNothing(func):
    """ decorator that avoid an exepction but send an mail """
    
    def wrap(self, *arg, **args):
        
        if hasattr(self, 'alive'):
            if self.alive is True:
                return func(self, *arg, **args)
            
    return wrap


def getPerfFile(perf_dir):
    """ return the perf file for reporting time"""

    if not os.path.exists(perf_dir):
        raise Exception('%s doesnt exists' % perf_dir)
    else:
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        day = date.day
        path = perf_dir
        for x in (year, month):
            path = os.path.join(path, str(x))
            if not os.path.exists(path):
                os.mkdir(path)
        path = os.path.join(path, "perf_%s.log" % day)
        if not os.path.exists(path):
            f = open(path,'w')
        else:
            f = open(path, 'a')
        return f

def getArchiveDirectory(dir):
    if not os.path.exists(dir):
        raise Exception('%s doesnt exists' % dir)
    else:
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        path = dir
        for x in (year, month):
            path = os.path.join(path, str(x))
            if not os.path.exists(path):
                os.mkdir(path)
        return path



class Worker(threading.Thread):

    def __init__(self, queue):
        self.__queue = queue
        threading.Thread.__init__(self)

    def run(self):
        while 1:
            elt = self.__queue.get()
            if elt is None:
                break # reached end of queue
            (func,args)  = (elt[0],elt[1:])
            func(*args)
            ## signals to queue job is done
            ## not for python24
            ## self.__queue.task_done()
            
def queue_tasks(tasks):
    ##be sure that task is an list
    tasks = [x for x in tasks]
    queue = Queue.Queue(len(tasks))
    [Worker(queue).start() for x in xrange(len(tasks))]
    for task in tasks:
        queue.put(task)
    [queue.put(None) for x in xrange(len(tasks))]
    #wait on the queue until everything has been processed  
    #queue.join()
    while threading.activeCount() != 1:
         time.sleep(.1)
    return


class HTTPException(Exception):

    def __init__(self, url, errcode,errmsg):
        self.url = url
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self):
        return "%s - %s : %s" % (self.url, self.errcode, self.errmsg)


class myURLOpener(urllib.FancyURLopener):
    # read an URL, with automatic HTTP authentication



    def http_error_default(self, url, fp, errcode,errmsg, headers):
        errcode = str(errcode)
        if errcode.startswith('4') or errcode.startswith('5'):
            raise HTTPException(url, errcode, errmsg)

    def setpasswd(self, user, passwd):
        self.__user = user
        self.__passwd = passwd

    def prompt_user_passwd(self, host, realm):
        return self.__user, self.__passwd


    def check(self, login, passwd,  service, url, timeout = None):
        url = DIRECT_URL % (login, passwd, service.machine,
                         service.port, url)
            
        
        try:
            self.open(url, timeout = timeout)
            service.status = service.status and True
        except Exception:
            logger.critical("CHECK %s failed : %s" % (url, self.elapse))
            logger.exception('error in %s' % url)
            service.status = False

    def open( self, fullurl, data=None, timeout = None):
        t = time.time()
        r = urllib.FancyURLopener.open(self, fullurl, data)
        self.elapse = time.time() - t

        logger.info("CALL %s elapse : %f" % (fullurl , self.elapse))
        
        if timeout and  self.elapse > float(timeout) :
            logger.error("Open %s failed : take to more time (%f>%s)" % \
                         (fullurl,
                          self.elapse,
                          timeout))
            raise HTTPException(fullurl , '408', 'Request Timeout')
        return r
            
            

class Service(object):

    interface.implements(interfaces.IWindowsService)
    
    __alive = None


    def __init__(self, machine, name, ip = None):
        self.service_name = name
        self.ip = ip
        self.machine = machine

            

    @property
    @ifIsDeadDoNothing
    def isRunning(self):
        status = QueryServiceStatus(self.service_name,
                                     machine = self.ip or self.machine)
        if status[1] == 4:
            return True
        else:
            return False

    @property
    @ifIsDeadDoNothing
    def isStopped(self):
        status = QueryServiceStatus(self.service_name,
                                    machine = self.ip or self.machine)
        if status[1] == 1:
            return True
        else:
            return False

    @clear
    @no_raise
    @ifIsDeadDoNothing
    def start(self):
        if self.isStopped:
            return StartService(self.service_name,
                                machine = self.ip or self.machine)
    @clear
    @no_raise
    @ifIsDeadDoNothing
    def restart(self):
        if self.isRunning:
            return RestartService(self.service_name,
                                  machine = self.ip or self.machine,
                                  waitSeconds = 120)
        if self.isStopped:
            return StartService(self.service_name,
                                machine = self.ip or self.machine)

    @clear
    @ifIsDeadDoNothing
    def stop(self):
        if self.isRunning:
            return StopService(self.service_name, machine = self.ip or \
                               self.machine)

    @property
    def alive(self):
        if self.__alive is not None:
            return self.__alive
        (f, path) = tempfile.mkstemp()
        try:
            ret = subprocess.call(self.ping_command + [self.ip or self.machine,],
                                  stdout = f,
                                  stderr = subprocess.STDOUT)
        except:
            ## there is a bug for python2.4 in subprocess call
            ## if we can check ping we return true
            ## http://bugs.python.org/issue1467770
            ret = 0
            return True
            
        if ret == 0:
            self.__alive = True
            return True
        ## log info about ping command
        logger.debug(open(path).read())
        logger.critical('%s (%s) is down , can\'t ping' % \
                        (self.machine, self.ip))
        self.__alive = False
        return False
        


class Server(object):

    interface.implements(interfaces.ITCPServer)

    status = False
    ping_command = None 
    __canConnect = None
    

    def __init__(self, machine, port):
        self.machine = machine
        self.port = port

    def clear(self):
        self.__canConnect = None
        self.__alive = None

    @property
    def canConnect(self):
        """ test an telnet on host:port """
        if self.alive is False:
            self.status = False
            return False
        if self.__canConnect is not None:
            return self.__canConnect
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__canConnect = False
        self.status = False
        try:
            t = 0
            while t<3:
                try:
                
                    s.connect((self.ip or self.machine, self.port))
                    logger.debug('%s <%s:%s> is LISTEN' % (self.name,
                                                           self.machine,
                                                           self.port))
                    self.__canConnect = True
                    ### init status if we can connect the status is False
                    self.status = True
                    break
                except:
                    pass
                logger.debug('retry for %s' % self.name)
                t += 1
                sleep(1)
            if t == 3:
                logger.critical('%s cant connect' % self.name)
            
        finally:
            s.close()
        return self.status

    
    def __str__(self):
        return '<%s:%s %s>' % (self.machine,
                               self.port,
                               self.canConnect)



class ClusterException(Exception):
    """ to deal for exception """


class TCPServer(Service, Server):


    def __init__(self, name, machine, service_name, port, ip = None,
                  rotate_logs = '',
                 **kwargs):
        self.name = name
        self.machine = machine
        self.service_name = service_name
        self.ip = ip
        self.port = int(port)
        self.rotate_logs = rotate_logs

class HttpServer(TCPServer):
    """ httpserver is just an tcpserver """
    


class ZeoClient(TCPServer):

    interface.implements(interfaces.IZeoClient)

    ## for log time for request
    perf_file = None

    def __init__(self, name, machine, service_name, connect_info,
                 feedcache = 'feedCache',
                 ip = None,
                 port = 8080, pool = 0, max_process_size = 0,
                 critical_errors = '',
                 log_file = '', rotate_logs = '', **args):
        """@args machine :machine of the service,
                 service_name : the service name in windows services,
                 ip : the ip of the machine,
                 port : the port on wich this zeoclient listen,
                 pool : the pool id of this zeoclient (1 or 2) for
                 restart cluster for liv"""
        
        self.name = name
        self.machine = machine
        self.service_name = service_name
        self.ip = ip
        self.connect_info = connect_info
        self.feedcache_url = feedcache
        self.critical_errors = critical_errors
        self.pid_file = args.get('pid_file',None)
        try:
            self.log = open(log_file,'rb')
        except:
            logger.critical('Cant open log file %s for %s' % (log_file,
                                                              name))
            self.log = None
                            
        self.port = int(port)
        self.pool = int(pool)
        self.__pid = 0
        self._mem = 0
        self.max_process_size = float(max_process_size)
        key = self.ip or self.machine
        
        try:
            wmi[key] = WMI(key).Win32_Process()
        except:
            logger.critical('No wmi interface for %s' % key)
        self.rotate_logs = rotate_logs
        #self.check()

    @property
    def process(self):
        key = self.ip or self.machine
        if self.alive:
            return [x for x in wmi.get(key,[]) if x.ProcessId == self.pid]

    def isInPool(self):
        return self.pool in (1, 2)

    def check(self):
        self.status = self.canConnect
        return self.status

    def feedcache(self):
        return self.url(self.feedcache_url, timeout=None)
        

    @property
    def pid(self):
        if self.__pid:
            return self.__pid
        ## now get pid by Z2.pid
        if self.pid_file and os.path.exists(self.pid_file):
            try:
                self.__pid = int(open(self.pid_file).read())
                self.status = self.status and True
            except:
                self.__pid = -1
                self.status = False

        
    @property
    @no_raise
    def mem(self):
        if self._mem :
            return self._mem
        if not self.canConnect:
            return
        machine = self.ip or self.machine
        process = self.process
        if process:
            self._mem = float(process[0].WorkingSetSize) / 1024
            if self._mem > self.max_process_size:
                logger.critical('memory is not good for %s : %s' %(self.name, 
                                                                   self._mem))
                self.status = False
        return self._mem

    @no_raise
    def search(self, pattern = None):
        if self.log is None or self.alive is False:
            return
        
        p = re.compile(self.critical_errors)
        s = None
        if pattern:
            s = re.compile(pattern)
        for r in rlines(self.log):
            if p.search(r):
                
                logger.critical('%s : %s' % (self.name,r))
                self.status = False
                break
            if s and s.search(r):
                logger.info('%s:%s' % (self.name, r) )
            if STOP_SEARCH in r:
                logger.info('last start %s : %s' % (self.name, r))
                break
                             
        
    def url(self, method, timeout = None):
        c = self.connect_info
        if self.canConnect:
            base = BASE % (c['public_name'],
                           c['entity'])
            urlopener = myURLOpener()
            urlopener.setpasswd(c['login'], c['passwd'])
            
            url = URL % (c['login'], c['passwd'], self.machine,
                         self.port,
                         base,
                         method)
            logger.info("CALL %s" % url)
            try:
                ## use for log
                now = datetime.datetime.now()
                ## raise an critical error if time to get url > timeout
                urlopener.open(url, timeout = timeout)
                if self.perf_file:
                    if 'VirtualHostRoot/' in url:
                        furl = url[url.index('VirtualHostRoot/') + \
                                   len('VirtualHostRoot/'):]
                    else:
                        return furl
                    self.perf_file.write("%s;%s;%s;%s;%s;%0.3f;\n" % \
                                         (now.isoformat(),
                                          self.machine,
                                          self.name,                                                                      self.mem,
                                          furl,
                                          urlopener.elapse))
                                                     

                self.status = self.status and True
            except Exception, e:
                logger.critical('error in %s : %s' % (url, e))
                
                self.status = False
            logger.info("END %s" % url)
        return self.status


class ZeoServer(TCPServer):

    interface.implements(interfaces.IZeoServer)

    def __init__(self, machine, service_name, port, ip=None,
                 rotate_logs = '',
                 **args):
        """@args machine :machine of the service,
                 service_name : the service name in windows services,
                 ip : the ip of the machine,
                 port : the port on wich this zeoclient listen,
                 pool : the pool id of this zeoclient (1 or 2) for
                 restart cluster for liv"""
        self.name = 'ZeoServer'
        self.machine = machine
        self.service_name = service_name
        self.ip = ip
        self.port = int(port)
        self.rotate_logs = rotate_logs




class Squid(TCPServer):

    interface.implements(interfaces.IHttpProxy)

    def __init__(self, machine, service_name, port, cache_dir, exe, conf,ip = None,  rotate_logs = [],
                 **kwargs):
        self.name = 'Squid'
        self.machine = machine
        self.service_name = service_name
        self.ip = ip
        self.port = int(port)
        self.exe = exe
        self.conf = conf
        self.cache_dir = cache_dir
        self.rotate_logs = rotate_logs

    def purge(self):
        """ purge squid """
        logger.info('squid stop')
        self.stop()
        while self.isStopped is False:
            sleep(0.1)
        logger.info('write to swap state')
        ## rename cache dir
        if os.path.exists(self.cache_dir):
            os.rename(self.cache_dir,self.cache_dir + 'old')
        logger.info('call %s',' '.join([self.exe, '-f', self.conf, '-z']))
        subprocess.call([self.exe, '-f', self.conf, '-z'])
        logger.info('start squid')
        self.start()
        ## delete cache dir
        shutil.rmtree(self.cache_dir + 'old')

        
  


class Pound(TCPServer):
    
    interface.implements(interfaces.IBalancer)

    def __init__(self, machine,
                 port,
                 service_name,
                 conf,
                 zeoclients, ip=None, **kwargs):
        self.name = 'Pound'
        self.machine = machine
        self.service_name = service_name
        self.port = int(port)
        self.ip = ip
        self.zeoclients = zeoclients
        #import pdb;pdb.set_trace();
        try:
            self.time_to_sleep = int(kwargs.get('time_to_sleep',20))
        except:
            self.time_to_sleep = 0
        try:
            self.config = conf
            f = open(self.config, 'rw')
            f.close()
        except:
            raise ClusterException("Fatal can't open config file for pound"
                                   ":<%s>" %\
                                   conf)

    def goodzeoclients(self):
        return [x for x in self.zeoclients if x.check() is True]

    def badzeoclients(self):
        return [x for x in self.zeoclients if x.check() is False]
        
    def restart_zeoclient(self, zeoclients, zeoclientsNotInPool=[]):
        """ restart zeoclients """
        backends = [x.name for x in zeoclients]
        if not backends:
            logger.info('NO zeoclients to restart , do nothing')
            return
            
        self.comment(zeoclients)
        self.restart()
        logger.info('pound is restarted : no connection to backend %s' %
                      ', '.join(backends))
        

        def restart(client):
            
            if client.alive is False:
                logger.info('cant restart client %s because %s is down' % \
                            (client.name, client.machine))
            else:   
                client.restart()
                logger.info('%s is restarted' % client.name)

            return client

        def check(client):
            client.check()
            logger.info('%s is checked : status %s' % (client.name,
                                                       client.status))
            return client

        def feedcache(client):
            client.feedcache()
            logger.info('FEEDCACHE %s : status %s' % (client.name,
                                                      client.status))
            return client

        

        if self.time_to_sleep == 0:
            ## we start all in one time
            def queue_zeoclient():
                for client in zeoclients:
                    yield (restart, client)
            queue_tasks(queue_zeoclient())
        else:
            ## because of conflict error on startup of zope
            ## enable-product-installation dont work
            for client in zeoclients[:-1]:
                restart(client)
                sleep(self.time_to_sleep)
            ## restart the last client
            restart(zeoclients[-1])
        
        def queue_check():
             for client in zeoclients:
                yield (check, client)

        queue_tasks(queue_check())
        
        ## feed cache
        good = [client for client in zeoclients if client.status == True]

        def queue_feedcache():
            for client in good:
                yield (feedcache, client)

        queue_tasks(queue_feedcache())
        
        bad_backends = [x for x in self.zeoclients if x.status == False]
        to_comment = bad_backends + zeoclientsNotInPool
        self.comment(to_comment)
        self.restart()
        logger.info('pound IS NOW RESTART')
        logger.info('pound (NOT IN POOL) :'
                    ' %s' %
                      ', '.join([x.name for x in to_comment]))

        if bad_backends:
            logger.error('there is %s bad backends : please check %s' \
                          % (len(bad_backends),
                             ', '.join([x.name for x in bad_backends])))

    def confForBackends(self, zeoclient):
        """ return an conf for a backend """

        return """
        BackEnd
        ### %s (%s) ###
        Address %s
        Port    %s
        End
        """ % (zeoclient.name, datetime.datetime.today().isoformat(),
            zeoclient.ip,
            zeoclient.port)

    def commentForBackends(self, zeoclient):
        """ return an conf for a backend """

        return """
        #BackEnd
        ### %s (%s) ###
        #Address %s
        #Port    %s
        #End
        """ % (zeoclient.name, datetime.datetime.today().isoformat(),
            zeoclient.ip,
            zeoclient.port)

    def remove(self, zeoclients):
        """ remove zeoclients from the pool """
        
        self.comment(zeoclients)
        self.restart()
        logger.info('pound IS NOW RESTART')
        logger.info('pound (NOT IN POOL) :'
                    ' %s' %
                      ', '.join([x.name for x in \
                                 set(zeoclients)\
                                  .union(set(self.badzeoclients()))]))

    def comment(self, backends):
        """ @backends : a list of zeolient """
        to_comment = set(backends).union(set(self.badzeoclients()))
        
        to_add = set(self.zeoclients).difference(set(backends))
        new_conf = ''
        for b in to_add:
            logger.info("Backend %s is now in Pound" % b.name)
            new_conf += self.confForBackends(b)
        for b in to_comment:
            logger.info("Backend %s is commented in Pound" % b.name)
            new_conf += self.commentForBackends(b)
        f = open(self.config, 'r')
        current_conf = f.read()
        f.close()
        ## erase all backends ###
        current_conf = BACKEND.sub('', current_conf)
        current_conf = BLANK_LINE.sub('', current_conf)
        current_conf = current_conf.replace('Service', "Service\n" + new_conf)

        f = open(self.config, 'w')
        f.write(current_conf)
        f.close()



class CheckServer(object):

    interface.implements(interfaces.IChecker)
    component.adapts(interfaces.ITCPServer)

    def __init__(self, server):
        self.server = server

    def check(self):
        return self.server.canConnect

#gsm.registerAdapter(CheckServer, ( interfaces.ITCPServer ,),
#                    interfaces.IChecker)
component.provideSubscriptionAdapter(CheckServer)
 

class CheckZeoclient(object):

    interface.implements(interfaces.IChecker)
    component.adapts(interfaces.IZeoClient)

    url = ''
    timeout = 10
    
    def __init__(self, client):
        self.client = client

    def check(self):
        
        self.client.url(self.url, self.timeout)
        self.client.search()
        logger.info('%s %s k : status %s' % (self.client.name,
                                             self.client.mem,
                                             self.client.status))
        
        
#gsm.registerAdapter(CheckZeoclient, ( interfaces.IZeoClient ,),
#                    interfaces.IChecker)
component.provideSubscriptionAdapter(CheckZeoclient)

        

class Cluster(object):
    """ definition of a cluster object
    An cluster have an fronts serveur and backend server (zeoclient)
    
    """

    interface.implements(interfaces.ICluster)

    config = {}

    def __init__(self, config):

        self.config = r = config
        self.zeoclients = []
        self.frontends = [] 
        
        ## constructs zeoclients
        #import pdb;pdb.set_trace();
        for zeoclient in r.get('cluster', 'zeoclients').split(','):
            section = zeoclient.strip()
            try:
                args = dict(r.items(section))
            except:
                logger.error('there is no zeoclients named %s,'
                             ' please check your configuration file' % section)
                sys.exit(-1)
                
            args['name'] = section
            args['connect_info'] = dict(r.items('connect'))
            args['feedcache'] = r.get('feedcache', 'url')
            self.zeoclients.append(ZeoClient(**args))
        for frontend in r.get('cluster', 'frontend').split(','):
            section = frontend.strip()
            args = dict(r.items(section))
            args['name'] = section
            args['connect_info'] = dict(r.items('connect'))
            args['feedcache'] = r.get('feedcache', 'url')
            args['zeoclients'] = self.zeoclients
            s = getattr(getmodule(self),args['type'])(**args)
            self.frontends.append(s)
            setattr(self, section, s)

    @property
    def services(self):
        """ return services in clusters """
        return self.zeoclients + self.frontends

    @property
    def balancer(self):
        """ return the balancer """
        for x in self.frontends:
            if interfaces.IBalancer.providedBy(x):
                return x

    @property
    def proxy(self):
        """ return the proxy server """
        for x in self.frontends:
            if interfaces.IHttpProxy.providedBy(x):
                return x
        
    def check(self, services = list(), url = None ,  **args):
        """ main checking service
        @param services: a list of name of services (see ini file)
        @param url: the url use to check
        
        for each services in list do the things as follows :
        1 - check url (/) for each server
            if server is an zeoclient -> check the homepage
            else check /
            if time to response < timeout (in ini file) : check is false
        3 - check all memory of all zeoclient
        2 - search in log file critical string for each zeoclient
        
        """

        timeout = self.config.get('DEFAULT', 'timeout')
        CheckZeoclient.timeout = timeout
        must_check_all = False
        if not services:
            must_check_all = True
        if url:
           CheckZeoclient.url = url
            
        if not must_check_all:
            services_to_check = [x for x in self.zeoclients if \
                                     x.name in services] + \
                                     [ x for x in \
                                       self.frontends if\
                                       x.name in services]
        else:
            #services_to_check = self.zeoclients
            services_to_check = self.services
        ##--- checking frontends ---
        ## warning - I dont know but zca dont like that with thread
        def check(service):
            for adapter in component.subscribers([service],
                                                 interfaces.IChecker):
                adapter.check()
        ## sync check        
        for client in services_to_check:
            check(client)
        

    def repair(self, services = None, url = '', **args):
        """
        Try to repair cluster
        @params services : the name of service to repair
        @params url : the url that serve to check the cluster

        first check all service of the cluster.
        All server wich have false status must be restarted
        """
        
        self.check(url = url)
        to_repair = [x.name for x in self.services \
                                          if x.status == False]
        ## reinit connection
        ## call start process
        self.start(services = to_repair, repair = True)

    def mem(self, services = None, url='', **args):
        """ get memory for service via wmi """
        
        if services:
            services = [x for x in self.zeoclients if \
                                 x.name in services]
        else:
            services = self.zeoclients

        def callback(client):
            logger.info('%s : mem %s k' % (client.name,
                                           client.mem))
            

        def call(client):
            print '%s : mem %s k' % (client.name,
                                     client.mem)
            return client

        for client in services:
            callback(call(client))


    def log(self, services = None, pattern = None, **args):
        """
        search in log
        @params  services -> the list of services to search
        @pattern -> a valid pattern
        """
        
        if services:
            services = [x for x in self.zeoclients if \
                                 x.name in services]
        else:
            services = self.zeoclients
        
        for service in services:
            service.search(pattern)

    def purge(self, **args):
        """
        purge squid
        """
        
        logger.info('purge proxy')
        self.proxy.purge()


    def rotate(self, services = None, **args):
        """
        rotate_logs and put it in an archive directory
        """
        
        if services:
            clients = [x for x in self.zeoclients if \
                                 x.name in services]
            fronts = [x for x in self.frontends if \
                                 x.name in services]
        else:
            clients = self.zeoclients
            fronts = self.frontends
        
        def logs():
            for s in (clients + fronts):

                if hasattr(s, 'rotate_logs'):
                    logs = [x.strip() for x in s.rotate_logs.splitlines() if x]
                    for log in logs:
                        yield (s , log)
        try:
            archivedir = self.config.get('cluster','archivedir')
        except:
            logger.error('cant rotate logs beacause there is no archivedir')
        dir_name = getArchiveDirectory(archivedir)
        
        for (s,log) in logs():
            ## we rotate logs of front
            
            file_name = os.path.basename(log)
            ## first copy log in dir_name
            new_name = '%s-%s-%s' % (s.name,
                                         time.strftime('%d-%H-%M-%S'),
                                         file_name)
            dst = os.path.join(dir_name, new_name)
            logger.info('rotate  %s to %s' % (file_name ,new_name))
            shutil.copy(log, dst)
            ## now we rotate the dst
            ## and we do an rotation
            
            try:
                f = open(log, 'w')
                f.write('')
                f.close()
            except:
                logger.error('Cant rollover file %s' % dst)

    def outofpool(self, zeoclients = None, **args):
        if not zeoclients:
            zeoclients = self.zeoclients
        balancer = self.balancer
        if balancer:
            balancer.remove(zeoclients)
            balancer.restart()
            
        
            

    def stop(self, services = None, **args):
        """
        stop services, if service is an zeoclient and zeoclient is in pool
        we comment this zeoclient from the pool
        """
        if not services:
            services = self.services
        else:
            services = [x for x in self.services if x.name in services]

        zeoclients = [x for x in services \
                      if interfaces.IZeoClient.providedBy(x)]
        
        self.outofpool(zeoclients)
        
        def stop(service):
            service.stop()
            
        def queue():
            for client in services:
                yield (stop, client)
        
        queue_tasks(queue())

        

    def start(self, services = None, withpurge = False, withrotate = False,
              repair = False,  **args):
        """
        action to start or restart services in cluster
        @params services : the list of services to restart
        @params withpurge : if true, squid is purge
        @params repair : if true call start by repair
        """
        
        must_restart_all = False
        if not services and not repair:
            must_restart_all = True

        ## check front end
        if withrotate:
            self.rotate()
            
        def restart(service):

            if not service.canConnect \
                   or service.name in services:
                logger.info('Restart %s' % \
                            service.name)
                if service.alive is False:
                    logger.error("Can't Restart %s because "
                                 "the machine is down"  % \
                                service.name)
                else:
                    if service.isRunning:
                        service.restart()
                    else:
                        service.start()
                    
        for front in self.frontends:
            if interfaces.IHttpProxy.providedBy(front) and withpurge == True:
                front.purge()
            else:
                restart(front)
            
        balancer = self.balancer
        if not self.zeoclients:
            return
        if balancer is not None:
            if must_restart_all is True:
                ## start by pool to avoid service interuption
                balancer.restart_zeoclient([x for x in self.zeoclients \
                                                 if x.pool == 1],
                                                [x for x in self.zeoclients \
                                                 if x.pool == 2])
                logger.info('pool 1 is restarted')
                balancer.restart_zeoclient([x for x in self.zeoclients \
                                              if x.pool == 2],
                                         )
                logger.info('pool 2 is restarted')
            else:
                services_to_start = [x for x in self.zeoclients if \
                                     x.name in services]
                logger.info('restart services <%s>' % ', '.join([str(x) \
                                                                 for x in \
                                                          services_to_start]))
                balancer.restart_zeoclient(services_to_start)
        else:
            ## no balancer available
            if must_restart_all is True:
                zeoclients =   self.zeoclients
            else:
                zeoclients = [x for x in self.zeoclients if \
                                     x.name in services]
            for client in zeoclients:
                restart(client)
            
                    
                


dirname = os.getcwd()
parser = OptionParser()
parser.add_option("-a", "--action", dest="action",
                  help="action to do : start, check, repair, mem, log, purge, rotate")
parser.add_option("-v", "--verbose", dest="verbose",
                  action="store_true",
                  help="see log in console")
parser.add_option("-c", "--config", dest="config",
                  help="config file. Default: %s" \
                  % os.path.join(dirname,
                                 'cluster.ini'),
                  default=os.path.join(dirname, 'cluster.ini'))
parser.add_option("-s", "--services", dest ="services",
                  help="do action for this service, you can add multiple"
                  "service in order to start, if there is no services "
                  "action is considered as global, ie -a start without -s,"
                  " all service are started", default=[])
parser.add_option("-u", "--url", dest ="url",
                  help="give an url to check",
                  default='/')
parser.add_option("-r", "--remove", dest ="remove",
                  help="remove lockfile", action="store_true"
                  , default=True)
parser.add_option("-p", "--pattern", dest ="pattern",
                  help="pattern to search in log"
                  , default=None)
parser.add_option("-P", "--purge", dest ="withpurge",
                  help="purge squid when starting cluster", action="store_true",
                  )
parser.add_option("-R", "--rotate", dest ="withrotate",
                  help="rotate log when starting cluster", action="store_true",
                  )


def main():
    """ a super controler for dpl cluster """

    (options, args) = parser.parse_args()
    config = ConfigParser()
    try:
        config.readfp(open(options.config))
    except IOError:
        parser.error("%s is not a valid config file (-h for see all options)"\
                     % (options.config))
        return

    if options.action is None:
        parser.error("action is required (-h for see all options)")
        return
    filename=config.get('DEFAULT', 'logfile')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter(\
        '%(asctime)s  %(levelname)-s: %(message)s')
    
         
    handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes = 1024 * 1024 * 10,
        backupCount = 5,
        )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logging.getLogger('').handlers = list()
    
    logger.addHandler(handler)
    
    toaddrs = config.get('DEFAULT','toaddrs') and config.get('DEFAULT',
                                                             'toaddrs')\
                                                             .split(';') or None
    
    if toaddrs:
        handler = logging.handlers.SMTPHandler(mailhost= config.get('DEFAULT',
                                                                'mailhost') ,
                                               fromaddr = config.get('DEFAULT',
                                                                     'fromaddr'),
                                               toaddrs = toaddrs,
                                               subject=config.get('DEFAULT',
                                                                  'subject'))
    
        handler.setLevel(logging.CRITICAL)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    

    # if options.verbose:

    console = logging.StreamHandler()
    if options.verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.ERROR)

    formatter = logging.Formatter(\
            '%(asctime)s  %(levelname)-s: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info('BEGIN')
    Server.ping_command = config.get('DEFAULT','ping_command').split(' ')
    ZeoClient.perf_file = getPerfFile(config.get('DEFAULT','perfdir'))
    cluster = Cluster(config)
    
    lock_path = os.path.join(os.getcwd(),config.get('DEFAULT',
                                                    'lock_file'))
    
    
        
    if os.path.exists(lock_path):
        logger.info('LOCK FILE %s is present' % lock_path)
        pid = open(lock_path,'r').read()
        if isRunning(pid):
            return
        else:
            ### remove lock
            logger.info('Process %s is not present  remove LOCK FILE' % pid)
            os.remove(lock_path)
    lockable_actions =  ('stop', 'start', 'repair')
    try:
        if options.action in lockable_actions:
            f = open(lock_path,'w')
            f.write(str(os.getpid()))
            f.close()
        method = getattr(cluster, options.action)
        method(services = options.services, url = options.url, 
               pattern = options.pattern, withpurge = options.withpurge,
               withrotate = options.withrotate)
        logger.info('END')
        
            
    finally:
        if options.action in lockable_actions:
            os.remove(lock_path)
            logger.info('DELETE LOCK FILE %s ' % lock_path)
        pass
