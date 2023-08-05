.. -*- coding: utf-8 -*-

Execution
=========

When installation and configuration are done, you can start monitoring
services with the ctl script.

Critical Events
~~~~~~~~~~~~~~~

For each critical event, a mail is sent describing the event.
With `repair` action (see below) service will be restarted on a critical event.

A critical event can be :

 1 - no connection to a tcp server
 
 2 - an http error when retrieving url

 3 - the size of memory exced a max value

 4 - an anormally message is appeared in log file

 5 - timeout while retrieving data from a zeoclient

  

Arguments
~~~~~~~~~

**-a** : action done by the script on a critical event.

 .. note::
 
    this argument is required

You can choose from the next seven actions :

 - **start** : start or restart service

 - **stop** : stop service
      
 - **check** : check availabilty of services in the cluster
      
 - **repair** : Try to repair a service considered dead. This can be view as **check** + **start** actions on service with status == KO

 - **mem** : check memory of all zeoclients

 - **log** : search some patterns in log file and report results
    
    .. note::
     
     If you have multiple zeoclients it's a convenient method to find things in your log file.

   .. warning:: 

     Only lines until the last zope reboot are taken !!

 - **rotate** : do a log rotate according to the ini file. 

   .. warning::

     clt.exe must have write access to work.
     The process of log rotate is pretty simple :

      1 - first copy all log file on a destination (see :doc:`configuration <configuration>`)

      2 - erase all content of the log file (write an empty string on log).
      
 - **purge** : purge proxy cache .
 
      
**-v** : verbose mode

**-c** : path of ini file (by default cluster.ini)

**-s** : a list of services. Work with actions `mem`, `repair`, `rotate`, `log`, `start` and `check`

**-u** : override url for testing. Normaly, this is used to check the home page of the plone site (see [connect] section in  :doc:`configuration <configuration>`)

**-P** : in conjonction with start, this action purge proxy cache (if there is a proxy cache on the cluster)

**-R** : in conjonction with start, rotate logs of services


Use case
~~~~~~~~

Start or restart services
-------------------------

::

 ctl.exe -a start

.. warning::

 If no zeoclient is provided with -s parameter, then all zeoclients are restarted

**Examples**

* restart all zeoclients by pool.

 .. note::
   
   If there is a balancer section (ex : pound) then the process tries to stop and start client without service interruption.

 ::

  ctl.exe -a start -c <path_to_ini_file> 

* only restart zeoclients 1.1 and 1.2

 ::
 
  ctl.exe -a start -c <path_to_ini_file> -s zeoclient1.1, zeoclient1.2 


**The start procedure with pound balancer**

1 -  check if all frontends are there: apache, squid, pound and zeoserver. If one of the four servers is not available -> start
2 -  zeoclients are removed by editing the conf pound (pound is restarted) (see procedure manual) by pool (see pool configuration on each zeoclient section)
Zeoclient in pool 1 will be restarted before those in pool 2.

Each zeoclient is restarted by following this steps: 

  1 - remove zeoclient entry from pound configuration

  2 - restart pound

  3 - stop zeoclient

  4 - start zeoclient

  5 - check zeoclient

    1 - check connection

    2 - check http connection

    3 - check memory

    4 - check log files

  6 - launch a feed url : to load some heavy things on zeoclient (ex : catalog index, put in cache some heavy cache).

  7 - if status is ok , the zeoclient is reintegrated into the stream (restart pound)    

 .. note::

  All zeoclients are checked during the process. A died zeoclient is removed from the pound conf even if it was not provided as a parameter.

Checking service
----------------

-a check:

Ensures that all are present zeoclients or frontend by 
 1 - sending an http request 
 2 - checking the memory of all zeoclients and verified that none of them exceeds the maximum (set in the ini file in kb) 
 3 - Tests whether any critical error has been detected in the log file. With no -s argument, all zeoclients will be tested. With no -u argument, the home page will be tested.

**Example**


test all home page, verify memory of all zeoclients and checks  logs since the last reboot

 ::

 dplctl.exe -a check -c <path_to_ini_file>  

retrieve blank.gif on all zeoclients + logs checking + memory 
 
 ::

 dplctl.exe -a check -c <path_to_ini_file> -u blank.gif  

retrieve blank.gif on all zeoclients + logs checking + memory only on zeoclient1.1,zeoclient2.1  

 ::
 
 dplctl.exe -a check -c <path_to_ini_file> -u blank.gif -s zeoclient1.1,zeoclient2.1 

test apache and squid 

 ::

 dplctl.exe -a check -c <path_to_ini_file> -s apache,squid


Repair service
--------------

 :: 

 dplctl.exe -a repair:

Like `check` command but the service is restarted when a critical event is detected.


