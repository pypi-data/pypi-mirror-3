.. -*- coding: utf-8 -*-

Execution
=========

When installation and configuration is done, you can start monitoring
services with the ctl script

Critical Events
~~~~~~~~~~~~~~~

For each critical event a mail is sending which describe the event.
With repair action (see below) service that have an critical event will be restarted.

An critical event can be :

 1 - no connection to a tcp server
 
 2 - an http error when retrieving url

 3 - the size of memory exced a max value

 4 - an anormally message is appeared in log file

 5 - an anormaly time to retrieve data from a zeoclient

  

Arguments
~~~~~~~~~

**-a** : action to be done by the script 

 .. note::
 
    this argument is required

There is seven action that you can do with the script:

 - **start** : start or restart service

 - **stop** : stop service
      
 - **check** : check availabilty of services in the cluster
      
 - **repair** : try to repair services that are considered as dead. This can view as an **check** + **start** with services with status == KO

 - **mem** : check memory of all zeoclients

 - **log** : search in log some string pattern and report results
    
    .. note::
     
     If you have multiple zeoclients it's a convenient method to find things in your log file.

   .. warning:: 

     Only lines until the last zope reboot are taken !!

 - **rotate** : do a log rotate according the ini file. 

   .. warning::

     clt.exe must have write access to work.
     The process of log rotate is pretty simple :

      1 - first copy all log file on a destination (see :doc:`configuration <configuration>`)

      2 - erase all content of the log file (write an empty string on log).
      
 - **purge** : purge proxy cache .
 
      
**-v** : verbose mode

**-c** : path of ini file (by default cluster.ini)

**-s** : a list of service. Work with actions mem, repair, rotate, log, start and check

**-u** : override url for testing. Normaly this is the home page of the plone site that is check (see [connect] section in  :doc:`configuration <configuration>`)

**-P** : in conjonction with start , this action purge proxy cache (if there is an proxy cache on the cluster)

**-R** : in conjonction with start, rotate logs of services


Use
~~~

Start or restart services
-------------------------

::

 ctl.exe -a start

.. warning::

 If no zeoclients is provided as a parameter then all zeoclients are restarted

**Example**

* restart all zeoclients by pool.

 .. note::
   
   If there is an balancer section (ex : pound) then the process try to stop and start client without service interruption.

 ::

  ctl.exe -a start -c <path_to_ini_file> 

* only restart zeoclients 1.1 and 1.2


 ::
 
  ctl.exe -a start -c <path_to_ini_file> -s zeoclient1.1, zeoclient1.2 


**The procedure of a start with pound balancer**

1 -  verification that all fronts are there: apache, squid, pound, zeoserver. If one of the four servers is not available -> start
2 -  zeoclients are removed by editing the conf pound (to restart pound) (see procedure manual) by pool (see pool configuration on each zeoclient section)
Zeoclient in the pool 1 will be restarted and then those of pool2.

The procedure of each restart of zeoclient is:

  1 - zeoclient configuration is removed of pound configuration

  2 - restart pound

  3 - stop zeoclient

  4 - start zeoclient

  5 - check zeoclient

    1 - check connection

    2 - check http connection

    3 - check memory

    4 - check log files

  6 - launch an feed url : to load some heavy things on zeoclient (ex : catalog index, put in cache some heavy cache).

  7 - if status is ok , the zeoclient is reintegrated into the stream (restart pound)    

 .. note::

  zeoclients all are checked during the process. If a zeoclient died is removed from the conf pound even though he was not provided as a parameter.

Checking service
----------------

-a check:

Ensures that all are present zeoclients or frontend by 
 1 - sending an http request 
 2 - checking the memory of all zeoclients and verified that none of them exceeds the maximum (set in the ini file in kb) 
 3 - Tests whether any critical error has been detected in the log file. If there is no -s arguments, all zeoclients will be tested. If no -u argument this is the home page that will be tested

**Example**


test all home page, verify memory of all zeoclients and checks  logs since the last reboot

 ::

 dplctl.exe -a check -c <chemin_vers_fichier_ini>  

retrieve blank.gif on all zeoclients + logs checking + memory 
 
 ::

 dplctl.exe -a check -c <chemin_vers_fichier_ini> -u blank.gif  

retrieve blank.gif on all zeoclients + logs checking + memory only on zeoclient1.1,zeoclient2.1  

 ::
 
 dplctl.exe -a check -c <chemin_vers_fichier_ini> -u blank.gif -s zeoclient1.1,zeoclient2.1 

test apache and squid 

 ::

dplctl.exe -a check -c <chemin_vers_fichier_ini> -s apache,management


Repair service
--------------

 :: 

 dplctl.exe -a repair:

As check command but when there is an critical event , the service is restarted

