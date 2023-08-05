# -*- coding: utf-8 -*-
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
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from zope.interface import Interface
from zope.interface import Attribute


class IWindowsService(Interface):

    service_name = Attribute('name')
    ip = Attribute('ip')
    machine = Attribute('machine')
    isRunning = Attribute('isRunning')
    isStopped = Attribute('isStopped')
    
    def start():
        """ start winservice """

    def restart():
        """ retstart winservice """

    def stop():
        """ stop winservice """

class IMachine(Interface):

    ip = Attribute('ip')
    machine = Attribute('machine')

    def alive():
        """ check if machine is alive """

        

class IChecker(Interface):

    def check():
        """ check an service """


class ITCPServer(Interface):

    name = Attribute('name')
    machine = Attribute('machine')
    port = Attribute('port')
    canConnect = Attribute('canConnect')
    
class IZeoClient(ITCPServer):
    """ represents an zeoclient """

    max_process_size = Attribute('maximum memory')

class IZeoServer(ITCPServer):
    """ represents an zeo  """


class IServiceProvideLog(Interface):

    rotate_logs = Attribute("list of path of rotate log")

class IBalancer(Interface):

    zeoclients =  Attribute("list of zeoclients")
    
    def restart_zeoclient(zeoclients, zeoclientsNotInPool = []):
        """ restart zeocleints by pool """

class IHttpProxy(Interface):

    def purge():
        """ purge data for http proxy """

class ICluster(Interface):

    zeoclients = Attribute("zeoclients that are manage by a IBalancer")
    frontends =  Attribute("service that are manage by a ICluster")

    def check(services, url = None):
        """ check cluster """

    def repair(services, url = None):
        """ repair cluster """

    def mem(services, url= ''):
        """ get memory of a cluster """

    def log(services, pattern):
        """ search in log """

    def purge():
        """ purge proxy """

    
    def rotate():
        """ rotates logs """

    def start(services, withpurge = False, withrotate = False,
              repair = False):
        """
        action to start services in cluster
        @params services : the list of services to restart
        @params withpurge : if true,httpproxy is purge
        @params repair : if true call start by repair
        """
