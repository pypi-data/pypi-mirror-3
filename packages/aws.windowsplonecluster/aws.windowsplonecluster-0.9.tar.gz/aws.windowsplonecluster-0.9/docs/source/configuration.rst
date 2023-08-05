.. -*- coding: utf-8 -*-

Configuration
=============

In order to work, you must describe all elements (zeoclients, http server, balancer ...) in an ini config file.
By convention, this file will be named **cluster.ini**

This config file contains at least two sections :

 * DEFAULT 

 * cluster

 * connect

DEFAULT
-------

In this section, we define all the options globaly available in the script.

Example
~~~~~~~

::

 [DEFAULT]
 ## Where we log
 timeout=5
 logfile=ctl.log
 max_process_size=176000
 critical_errors=Zope
 lock_file=ctl.lock
 mailhost=smtp.free.fr
 fromaddr=
 toaddrs=
 subject=[ERROR] - There is an error
 ping_command=ping -n 1
 perfdir=/tmp
 archivedir=c:/logs

Description
~~~~~~~~~~~

Options are:
 
  * **timeout** - timeout of http response. If an url spends more time then the timeout, a critical error is raised (default 10sec)

  * **logfile** - the log file location

  * **max_process_size** - the max amount size of (what ??) a zeoclient can accept. If the process memory size reach this value, a critical error is raised

  * **critical_errors** - list of patterns considered as critical if found in the log file. Patterns are separeted by '|'. 

  * **lock_file** - the lock file location. This file is used to avoid conccurent access to critical job by controller's processes.

  * **mailhost** - smtp server name used to send alerts on critical error.

  * **fromaddr** - the from field of the mailed alert. 

  * **toaddrs** - recipients list for mailed alerts.
   
  * **subject** - the subject of the mail

  * **ping_command** - the ping command used to check host availability.
.. FIXME: Peut-Ãªtre utiliser node Ã  la place de host ?

  * **perfdir** - when checking url on zeoclient, the access time is logged in files. The log files are written in structured subdirs under perfdir : :: 
     
    $perfdir\YYYY\MM\

  * **archivedir** - The rotated logs are moved to this directory

Cluster
-------

This section is used to describe the zeoclient's cluster and the http server in front of it.

Example
~~~~~~~

::

 [cluster]
 ## Definition of the pool of zeoclients
 zeoclients = zeoclient1,zeoclient2,zeoclient3,zeoclient4,zeoclient5
 frontend = apache,squid,pound,management

Description
~~~~~~~~~~~

Each element of zeoclients and frontend lists must be a **reference** to a **section** declare in the *cluster.ini* file. So in the example above, we have **5 sections** that describe 5 zeoclients and **4 sections** that describe respectively apache , squid , pound and a zeoclient name *management*.

Connect
-------

This section is used to define credentials for testing connection on zeoclient.

.. warning::

   Use basic authentification for zeoclient connections.

Example
~~~~~~~

::

 [connect]
 login=admin
 passwd=admin
 entity=plone
 public_name=myplone.org

Description
~~~~~~~~~~~

 * **login** - login account
 * **passwd** - password
 * **public_name** - public name of the site
 * **entity** - name of plone site (for VHM request)
 
 
Zeoclient
---------

Describes a zeoclient.

Example
~~~~~~~

::
 
 [zeoclient]
 machine=myhost
 ip=192.168.0.6
 service_name=Zope_1794486424
 log_file=C:\work\instances\zeoclient1\log\event.log
 rotate_logs=
  C:\work\instances\zeoclient1\log\event.log
  C:\work\instances\zeoclient1\log\Z2.log
 pid_file=C:\work\instances\zeoclient1\log\Z2.pid
 port=8080
 pool=1
 type=ZeoClient 

Description
~~~~~~~~~~~

 * **machine** - dns machine name
 * **ip** - interface to connect to the machine for starting service.
.. FIXME: ip addr au lieu de interface ? Pareil pour tous les autres

 * **service_name** - the name of the service (see property in windows service application)
 * **log_file** - location of the log file. The path can be a shared network file ( \\myhost\sharing_directory\log\event.log )
 * **rotate_logs** - location of the log files rotated by the rotate process 
 * **pid_file** - used to check the memory process
 * **port** - used to check the connection to the zeoclient
 * **pool** - for the load balancer. Value can be 1 or 2.
 * **type** - ZeoClient -> important ! data used by the controller to choose the good checking process.

TCP server
----------

Use to monitor tcp servers in your architecture. Can be an IIS, Apache or every tcp server that can be started by a windows service (located on local or remote machine)

Example
~~~~~~~

::
 
 [apache]
 machine=youenn-0re1r3lw
 ip=127.0.0.1
 service_name = Apache2.2
 port=80
 type=TCPServer   


Description
~~~~~~~~~~~

 * **machine** - dns machine name
 * **ip** - interface to connect to the machine for starting service.
 * **service_name** - the name of the service (see property in windows service application)
 * **port** - use for checking the connection to the tcp server
 * **rotate_logs** - where are the logs to be rotated by the rotate process (FIXME: pas dans l'exemple)
 * **type** - must be `TCPServer`



Zeoserver
---------

Describe a zeoserver

::
 
 [zeoserver]
 machine=youenn-0re1r3lw
 ip=127.0.0.1
 service_name = Zeo_1794486424
 port=9090
 type=ZeoServer   


Description
~~~~~~~~~~~

 * **machine** - dns machine name
 * **ip** - interface to connect to the machine for starting service.
 * **service_name** - the name of the service (see property in windows service application)
 * **port** - use for checking the connection to the server
 * **rotate_logs** - location of the log files rotated by the rotate process
 * **type** - must be `ZeoServer`

Squid
-----

Squid is commonly used as reverse proxy for accelerated things.

.. warning::

   Be carreful, squid purge operation can be done only on the same **machine** which run **ctl.exe**. 

Example
~~~~~~~

::
 
 [squid]
 machine=youenn-0re1r3lw
 service_name = Squid
 ip=127.0.0.1
 port=3128
 cache_dir = c:\zope\squid\cache
 rotate_logs=
  c:\zope\squid\log\access.log
  c:\zope\squid\log\cache.log
  c:\zope\squid\log\store.log
 exe = c:\zope\squid\sbin\squid.exe
 conf = c:\zope\squid\etc\squid.conf
 type=Squid

Description
~~~~~~~~~~~

 * **machine** - dns machine name
 * **ip** - interface to connect to the machine for starting service.
 * **service_name** - the name of the service (see property in windows service application)
 * **port** - use for checking the connection to the web server
 * **cache_dir** - c:\zope\squid\cache
 * **rotate_logs** - location of the log files rotated by the rotate process
 * **exe** - location of the squid executable , use for the purge of cache.
 * **conf** - location of the squid confing file, use for the purge of cache.
 * **type** - must be `Squid`


Pound
-----

Pound is commonly used as load balancer. 

.. note::

   You can compile pound with Mingw or Cygwin on windows

.. warning::
  
   dplctl.exe must have a writting access because the config file is rewritten if you add or remove zeoclients.


Example
~~~~~~~

::
 
 [pound]
 machine=youenn-0re1r3lw
 ip=127.0.0.1
 port=8085
 service_name = Pound
 conf= c:\zope\balancer\pound.cfg
 type=Pound
 time_to_sleep = 40


Description
~~~~~~~~~~~

 * **machine** - dns machine name
 * **ip** - interface to connect to the machine for starting service.
 * **service_name** - the name of the service (see property in windows service application)
 * **port** - use for checking the connection to the web server
.. FIXME: erreur de copie/colle ?
 * **cache_dir** - c:\zope\squid\cache

 * **rotate_logs** - location of the log files rotated by the rotate process
.. FIXME: erreur de copie/colle ?
 * **exe** - where is the squid executable , use for the purge of cache.  

 * **conf** - location of the pound confing file. Used for QoS start of cluster.
 * **type** - must be `Pound`
.. FIXME: un oubli ?
 * **ty_to_sleep** - 


