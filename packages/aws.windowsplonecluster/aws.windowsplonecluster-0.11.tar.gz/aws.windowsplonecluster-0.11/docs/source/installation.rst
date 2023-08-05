.. -*- coding: utf-8 -*-

Installation
============

Without buildout
~~~~~~~~~~~~~~~~

 1 - Install distribute package : http://pypi.python.org/pypi/distribute#installation-instructions

 2 - Install virtualenv ::

  C:\work>easy_install virtualenv

 3 - Make an isolated python environment ::

  C:\work>virtualenv --distribute --no-site-packages testwpc
  New python executable in testwpc\Scripts\python.exe
  Installing distribute.........................................................
  ..............................................................................
  .............................................done.

 4 - Activate the new virtualenv ::

  C:\work\testwpc>Scripts\activate.bat
  (testwpc) C:\work\testwpc>

 5 - Install aws.windowsplonecluster ::

  (testwpc) C:\work\testwpc>Scripts\easy_install.exe aws.windowsplonecluster
  install_dir C:\work\testwpc\Lib\site-packages\
  Searching for aws.windowsplonecluster
  Reading http://pypi.python.org/simple/aws.windowsplonecluster/
  Reading https://github.com/yboussard/aws.windowsplonecluster
  Best match: aws.windowsplonecluster 0.6dev
  Downloading http://pypi.python.org/packages/source/a/aws.windowsplonecluster/aw s
  
 6 - Test controller script ::

  (testwpc) C:\work\testwpc>Scripts\ctl.exe -h
  usage: ctl-script.py [options]

  options:
   -h, --help            show this help message and exit
   -a ACTION, --action=ACTION
                        action to do : start, check, repair, mem, log, purge,
                        rotate
   -v, --verbose         see log in console
   -c CONFIG, --config=CONFIG
                        config file. Default: C:\work\testwpc\cluster.ini
   -s SERVICES, --services=SERVICES
                        do action for this service, you can add
                        multipleservice in order to start, if there is no
                        services action is considered as global, ie -a start
                        without -s, all service are started
   -u URL, --url=URL     give an url to check
   -r, --remove          remove lockfile
   -p PATTERN, --pattern=PATTERN
                        pattern to search in log
   -P, --purge           purge squid when starting cluster
   -R, --rotate          rotate log when starting cluster

Now, you can :doc:`configure <configuration>` the controller script 

With Buildout
~~~~~~~~~~~~~

 1 - Install distribute package : http://pypi.python.org/pypi/distribute#installation-instructions

 2 - Install virtualenv ::

  C:\work>easy_install virtualenv

 3 - Make an isolated python environment ::

  C:\work>virtualenv --distribute --no-site-packages testwpc
  New python executable in testwpc\Scripts\python.exe
  Installing distribute.........................................................
  ..............................................................................
  .............................................done.

 4 - Activate the new virtualenv ::

  C:\work\testwpc>Scripts\activate.bat
  (testwpc) C:\work\testwpc>

 5 - Install zc.buildout ::

  (testwpc) C:\work\testwpc>Scripts\easy_install.exe zc.buildout
  install_dir C:\work\testwpc\Lib\site-packages\
  Searching for zc.buildout
  Reading http://pypi.python.org/simple/zc.buildout/

 6 - Init buildout ::

  (testwpc) C:\work\testwpc>Scripts\buildout.exe init
  Creating 'C:\\work\\testwpc\\buildout.cfg'.
  Creating directory 'C:\\work\\testwpc\\bin'.
  Creating directory 'C:\\work\\testwpc\\parts'.
  Creating directory 'C:\\work\\testwpc\\eggs'.
  Creating directory 'C:\\work\\testwpc\\develop-eggs'.

 7 - Edit buildout.cfg and copy/paste this to it ::

  [buildout]
  parts = 
    wpc

  [wpc]
  recipe = zc.recipe.egg
  eggs =
      aws.windowsplonecluster
     
 8 - Run buildout ::

  (testwpc) C:\work\testwpc>bin\buildout.exe
  Upgraded:
  zc.buildout version 1.5.2;
  restarting.
  Generated script 'C:\\work\\testwpc\\bin\\buildout'.
  Getting distribution for 'zc.recipe.egg'.
  install_dir C:\work\testwpc\eggs\tmpzlaadp
  Got zc.recipe.egg 1.3.2.
  Installing wpc.
  Generated script 'C:\\work\\testwpc\\bin\\ctl'.

 .. warning::
 
   There is an dependance with WMI (http://pypi.python.org/pypi/WMI/1.4.9).
   If you have a problem in installation of WMI I recommand to install it with pip on your system

 .. warning::

   If you use aws.windowsplonecluster with an old zope2 server, then zope.component and zope.interface are
   fake egg. 
   Add this in wpc section 

   extra-paths =
     ${zope2:location}/lib/python 



 9 - Test controler script ::

  (testwpc) C:\work\testwpc>bin\ctl.exe -h
  usage: ctl-script.py [options]

  options:
   -h, --help            show this help message and exit
   -a ACTION, --action=ACTION
                        action to do : start, check, repair, mem, log, purge,
                        rotate
   -v, --verbose         see log in console
   -c CONFIG, --config=CONFIG
                        config file. Default: C:\work\testwpc\cluster.ini
   -s SERVICES, --services=SERVICES
                        do action for this service, you can add
                        multipleservice in order to start, if there is no
                        services action is considered as global, ie -a start
                        without -s, all service are started
   -u URL, --url=URL     give an url to check
   -r, --remove          remove lockfile
   -p PATTERN, --pattern=PATTERN
                        pattern to search in log
   -P, --purge           purge squid when starting cluster
   -R, --rotate          rotate log when starting cluster

Now, you can :doc:`configure <configuration>` the controller script 
