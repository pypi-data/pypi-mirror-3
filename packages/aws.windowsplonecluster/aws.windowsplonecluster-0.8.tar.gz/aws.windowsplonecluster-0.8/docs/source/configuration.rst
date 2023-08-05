.. -*- coding: utf-8 -*-

Configuration
=============

In order to work, you must describe all zeoclients , http server, balancer ... on a ini config file name by convention **cluster.ini**

There is on minimum two section :

 * DEFAULT 

 * cluster

 * connect

DEFAULT
-------

We define all options that are available for the script in general

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
 
  * **timeout** - timeout of http response. If an url spend more time of the timeout then an critical error is raised (default 10sec)

  * **logfile** - the location of the log file

  * **max_process_size** - the max amount size of an zeoclient can accept. If the process memory size reach this value, an critical is raised

  * **critical_errors** - string pattern separated by | that be considered as critical if the parsing of log file found it. 

  * **lock_file** - o avoid that two process of the controller do critical job in same time.

  * **mailhost** - for configure send mail

  * **fromaddr** - the from addrs

  * **toaddrs** - a list of recipients that are alerting when there is an critical alert on cluster
   
  * **subject** - the subject of the mail

  * **ping_command** - the ping system command in order to see if an machine is available

  * **perfdir** - when checking url on zeoclient , we reporting access time on log file. The structure of directory tree is like that :: 
     
    $perfdir\YYYY\MM\

  * **archivedir** - when we rotate logs , all logs go to this directory

Cluster
-------

You declare in this section your http server in front of the zeoclients cluster, and zeoclient that are in the cluster.

Example
~~~~~~~

::

 [cluster]
 ## Definition of the pool of zeoclient
 zeoclients = zeoclient1,zeoclient2,zeoclient3,zeoclient4,zeoclient5
 frontend = apache,squid,pound,management

Description
~~~~~~~~~~~

Each element of zeoclients and frontend list must be a **reference** of an **section** in the *cluster.ini* file. So in this example we have **5 sections** that describe 5 zeoclients and **4 sections** that describe respectively apache , squid , pound and a zeoclient name *management*.

Connect
-------

For testing connection on zeoclient.

.. warning::

   Use authentification basic for connecting to zeoclient

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

 * **login** - user login
 * **passwd** - password
 * **public_name** - public name of the site
 * **entity** - name of plone site (for VHM request)
 

 
 
Zeoclient
---------

Describe an zeoclient.

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
 * **service_name** - the name of the service (see property in windows service application)
 * **log_file** - where is the log file. If it is located in another machine we can get it via an share network file ( \\myhost\sharing_directory\log\event.log )
 * **rotate_logs** - where are the logs to be rotated by the rotate process 
 * **pid_file** - use for checking the memory process
 * **port** - use for checking the connection to the zeoclient
 * **pool** - for the load balancer. Value can be 1 or 2.
 * **type** - ZeoClient -> important ! tell to the controller script that this configuration is an ZeoClient. So the controller adapt the checking process to this type

TCP server
----------

Use for monitoring tcp server in your architecture. Can be an IIS, Apache or every tcp server that can be started by an windows service (located or not on the local machine)

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
 * **port** - use for checking the connection to the web server
 * **rotate_logs** - where are the logs to be rotated by the rotate process 
 * **type** - must be TCPServer



Zeoserver
---------

Describe an zeoserver

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
 * **port** - use for checking the connection to the web server
 * **rotate_logs** - where are the logs to be rotated by the rotate process 
 * **type** - must be ZeoServer

Squid
-----

Squid is commonly used as reverse proxy for accelerated things.

.. warning::

   Be carreful , squid purge operation can't be done only on the same **machine** which run **ctl.exe**. 

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
 * **rotate_logs** - where are the logs to be rotated by the rotate process 
 * **exe** - where is the squid executable , use for the purge of cache.
 * **conf** - where is the squid conf , use for the purge of cache.
 * **type** - must be Squid


Pound
-----

Pound is commonly used as load balancer. 

.. note::

   You can compile pound with Mingw or Cygwin on windows

.. warning::
  
   dplctl.exe must have an access on writing because the conf is rewritting if you add or remove zeoclients.


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
 * **cache_dir** - c:\zope\squid\cache
 * **rotate_logs** - where are the logs to be rotated by the rotate process 
 * **exe** - where is the squid executable , use for the purge of cache.
 * **conf** - where is the pound conf , use for QoS start of cluster.
 * **type** - must be Pound


