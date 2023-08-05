.. -*- coding: utf-8 -*-


.. aws.windowsplonecluster documentation master file, created by
   sphinx-quickstart on Wed Apr 20 11:10:55 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aws.windowsplonecluster
=======================

**GOAL**: have a supervisor alternative on Windows systems.

It allows you :

 - QOS restart, stop zeoclients with a load balancing (for the moment only pound is implemented).
           
          * During the reboot of a zeoclient, it is first out of the pool distribution, then restart, and check then if it's ok it back into the pool.

          * Users continue to browse the site. You can restart all zeoclients of the cluster. The site is always available during the reboot modulo the restart of the load balancer (two pool of zeoclients are configured)

 - To purge reverse proxy cache (for now only squid is implemented)

 - To monitor the cluster (testing url, reporting access times, sending mail if critical event occurs, monitoring memory)

 - To analyze the logs (as regular expressions) searching across the logs of all machines at once.

 - To repair a cluster when a critical event is detected (monitoring memory error on 500 test url, log file) -> + restart email alert component.

 - To rotate log of all the log files present on the cluster.

Contents:

.. toctree::
   :maxdepth: 2

   Installation <installation>
   Configuration <configuration>
   Use <execution>


* :ref:`search`

