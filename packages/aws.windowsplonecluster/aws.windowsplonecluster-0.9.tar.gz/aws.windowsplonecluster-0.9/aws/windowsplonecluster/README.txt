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
    ... [zeoclient]
    ... service_name=Zope_1794486424
    ... log_file=C:\instances\log\event.log
    ... port=8080
    ... type=ZeoClient"""
    >>> from StringIO import StringIO
    >>> config = StringIO(config)
    >>> c.readfp(config)
    >>> cluster = aws.windowsplonecluster.Cluster(c)
    
