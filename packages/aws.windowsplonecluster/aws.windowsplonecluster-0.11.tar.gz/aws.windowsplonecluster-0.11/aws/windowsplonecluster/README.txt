=======================
aws.windowsplonecluster
=======================

A super controler script for windows server for plone-squid-zeoclient cluster

    >>> import  aws.windowsplonecluster
    >>> from ConfigParser import ConfigParser
    >>> c = ConfigParser()

    >>> config = """
    ... [cluster]
    ... ## Definition of the pool of zeoclient
    ... zeoclients = zeoclient
    ... frontend = apache
    ... [apache]
    ... service_name = Apache2.2
    ... port=80
    ... type=HttpServer
    ... ip = 127.0.0.1
    ... machine = localhost
    ... [zeoclient]
    ... ip = 127.0.0.1
    ... machine = localhost
    ... service_name=Zope_1794486424
    ... log_file=C:\instances\log\event.log
    ... port=8080
    ... type=ZeoClient
    ...
    ... [connect]
    ... login=admin
    ... passwd=admin
    ... entity=dpl-dt
    ... public_name=preprod-pcispirit-dpl.loreal.wans
    ... [feedcache]
    ... url="""
    >>> from StringIO import StringIO
    >>> config = StringIO(config)
    >>> c.readfp(config)
    >>> cluster = aws.windowsplonecluster.Cluster(c)
    
