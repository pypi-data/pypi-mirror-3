==================================================
inqbus.ocf.generic : OCF resource agents framework 
==================================================

:Version: 0.1
:Download: http://pypi.python.org/pypi/inqbus.ocf.generic
:Keywords: python, OCF, resource agents, framework, pacemaker, 

.. contents::
    :local:

Overview
========

Inqbus.ocf.generic is a framework that helps you writing OCF compatible resource 
agents for e.g. the Pacemaker failover management system.

The inqbus.ocf.generic framework keeps away from you the gory details
you have to go into writing an OCF compatible resource agent.
Powerfull base classes bring to you:

* support of the complete set of OCF exitcodes and their respective business logik
* OCF Paramter classes for integer, string, etc. values
* predefined generic OCF handlers (meta-data, validate)
* the generation of the XML meta data is done for you automagically
* easy addition of handlers for e.g. start/stop/status
* inheritance of resource agents: encapsulate agent business logic and share it among similiar reasource agents

Installation
============

Please refer to the installation of the 
`inqbus.ocf.agents package <http://pypi.python.org/pypi/inqbus.ocf.agents>`_ .

Documentation
=============

The documentation of the inqbus.ocf.generic API is still in progress.
Please refere in the meanwhile to inqbus.ocf.agents which is a good example
of using inqbus.ocf.generic.

Credits
=======

I have stolen lots of ideas from Michael Samuel's 
`ocfra framework <https://code.launchpad.net/~therealmik/+recipe/python-ocfra-daily>`_ .

License                                                                                                                                                          
=======                                                                                                                                                          
                                                                                                                                                                 
This software is licensed under the New BSD License. See the LICENSE.txt file in                                                                                     
the top distribution directory for the full license text.
                 