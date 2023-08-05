======================================================================
inqbus.ocf.agents : Pacemaker OCF resource agents for daemon processes
======================================================================

:Version: 0.1
:Download: http://pypi.python.org/pypi/inqbus.ocf.agents
:Keywords: python, OCF, resource agents, pacemaker, openvpn, daemon process

.. contents::
    :local:

Overview
========

OCF compatible resource agent classes programmed in python.
This package includes some generic OCF agent classes for PID controlled daemons
like openvpn based on the `inqbus.ocf.generic <http://pypi.python.org/pypi/inqbus.ocf.generic>`_ framework.

The inqbus.ocf.generic framework keeps away from you the gory details
you have to go into writing an OCF compatible resource agent.
Powerfull base classes bring to you:

* support of the complete set of OCF exitcodes and their respective business logik
* OCF Paramter classes for integer, string, etc. values
* predefined generic OCF handlers (meta-data, validate)
* the generation of the XML meta data is done for you automagically
* easy addition of handlers for e.g. start/stop/status
* inheritance of resource agents: encapsulate agent business logic and share it among similiar reasource agents

Inqbus.ocf.agents in addition brings the following functionality

* the business logic for controlling the PID file
* checking for the running state of the PID
* starting and stopping the daemon (with checking for zombies and staggered kill signals to bring a process really down if it has to die)
* checking for the PID status

in the base class PIDBaseAgent.

The PIDAgent and Openvpn classes are derived from PIDBaseAgent with minimal
programming efford::

    from pidbaseagent import PIDBaseAgent
    from inqbus.ocf.generic.parameter import OCFString

    class PIDAgent(PIDBaseAgent):

        def add_params(self):
            self.add_parameter(OCFString("executable",
                                longdesc="Path to the executable",
                                shortdesc="executable",
                                required= True) )
            self.add_parameter(OCFString( "pid_file",
                                longdesc="Path to the pid file",
                                shortdesc="executable",
                                required= True) )

        def get_pid_file(self):
	    """tell the base class to find the PID file in the parameter 'pid_file'"""
            return self.params.pid_file.value

        def get_executable(self):
	    """tell the base class how to find the executable path in the parameter 'executable'"""
            return self.params.executable.value

    def main():
        """Entry point for the reasource agent shellscript"""
        import sys
        PIDAgent().run(sys.argv)

    if __name__ == "__main__" : main()
        """Entry point for the command line"""



To use the inqbus.ocf.agents agent classes you need to set only one symlink per
agent class into your Pacemaker (or other OCF HA) system.

Building arbitrary resource agent classes e.g. for IP addresses is
easy utilizing the inqbus.ocf.generic <http://pypi.python.org/inqbus.ocf.generic>_ framework.

Documentation
=============

This file and the source files for openvpn and the PIDAgent classes serve as a
simple introduction to inqbus.ocf.agents. For more in depth
documentation on writing your own reasource agents with the
inqbus.ocf framework, have a look at

* `inqbus.ocf.agents documentation http://packages.python.org/inqbus.ocf.agents <http://packages.python.org/inqbus.ocf.agents>`_
* `inqbus.ocf.generic ocf agent developer documentation http://packages.python.org/inqbus.ocf.generic <http://packages.python.org/inqbus.ocf.generic>`_

Requirements
============

Python >=2.7 or Python 3.x


Installation
============

We recomment a buildout based installation into a virtual environment
but you may install inqbus.ocf.agents via pip or easy_install as
well.

Installation via buildout
-------------------------

.. note::
    This installation guide asumes /opt/ocf as installation directory.
    Please adjust the installation directory to your needs.

Build a virtual environment::

    :/opt$ virtualenv --no-site-packages ocf
    :/opt$ cd ocf
    :/opt/ocf$ source bin/activate
    (ocf):/opt/ocf$

Install the make environment buildout and initialize it::

    (ocf):/opt/ocf$ easy_install zc.buildout
    (ocf):/opt/ocf$ ./bin/buildout init

Create a buildout.cfg::

    [buildout]                                                                                                                                                       
    parts = app                                                                                                                                                      
            pidagent                                                                                                                                                 
            openvpn                                                                                                                                                  
                                                                                                                                                                 
    # Buildout directories to use.                                                                                                                                   
    eggs-directory          = eggs                                                                                                                                   
                                                                                                                                                                 
    ###############################################################################                                                                                  
    # Download links for packages                                                                                                                                    
    # -----------------------------------------------------------------------------
    # Add additional egg download sources here.                                                                                                                      
    # Note that pypi.propertyshelf.com and mypypi.inqbus.de require authentication.                                                                                  
    find-links = http://mypypi.inqbus.de/privateEggs                                                                                                                 
                                                                                                                                                                     
    ###############################################################################
    # Extensions                                                                                  
    # -----------------------------------------------------------------------------
    # Load several extensions.
    extensions = lovely.buildouthttp                                                                                                                                                                
                                                                                                                                                                 
    [app]                                                                                                                                                            
    recipe = z3c.recipe.scripts                                                                                                                                      
    eggs = inqbus.ocf.agents                                                                                                                                         
    interpreter = python_ocf                                                                                                                                         
                                                                                                                                                                 
    [openvpn]                                                                                                                                                        
    recipe = collective.recipe.template                                                                                                                              
    output = ${buildout:directory}/bin/openvpn.sh                                                                                                                    
    inline =                                                                                                                                                         
        #!/bin/bash                                                                                                                                                  
        ${buildout:directory}/../bin/python ${buildout:directory}/bin/openvpn $*                                                                                     
    mode = 755                                                                                                                                                       
                                                                                                                                                                 
    [pidagent]                                                                                                                                                       
    recipe = collective.recipe.template                                                                                                                              
    output = ${buildout:directory}/bin/pidagent.sh                                                                                                                   
    inline =                                                                                                                                                         
        #!/bin/bash                                                                                                                                                  
        ${buildout:directory}/../bin/python ${buildout:directory}/bin/pidagent $*                                                                                    
    mode = 755                                                                     

run buildout to install the package::

    (ocf):/opt/ocf$ ./bin/buildout


Configuration
=============

First check the installation::

    (ocf):/opt/ocf$ ./bin/openvpn
    Usage: openvpn.py <start|validate-all|stop|monitor|meta-data>


.. note::
    You have to identify the OCF agent location of your OS to proceed.
    On Debian the OCF agents live under::

       /usr/lib/ocf/resource.d/

    Also you are free to set a provider directory for the agents. Here we asume as provider name ::

	inqbus

Integrating the openvpn agent class into Pacemaker::

    :/opt/ocf$ cd /usr/lib/ocf/resource.d/
    :/usr/lib/ocf/resource.d/$ mkdir inqbus
    :/usr/lib/ocf/resource.d/$ cd inqbus
    :/usr/lib/ocf/resource.d/inqbus$ ln -s /opt/ocf/bin/openvpn .

.. note::
    You may repeat this last line with other resource agent classes (also available yet: pidagent)::

        :/usr/lib/ocf/resource.d/inqbus$ ln -s /opt/ocf/bin/pidagent .

Now the configuration is complete an you can use the OCF python
resource agents as the others that came with heartbeat or pacemaker.

Testing with ocf-tester
=======================

You may use the dummy_daemon that comes with inqbus.ocf.agents to test the pidagent::
 
    :/opt/ocf/buildout$ ocf-tester -n test -o pid_file=/tmp/dummy_daemon.pid -o executable=./bin/dummy_daemon `pwd`/bin/pidagent.sh

License                                                                                                                                                          
=======                                                                                                                                                          
                                                                                                                                                                 
This software is licensed under the New BSD License. See the LICENSE.txt file in                                                                                     
the top distribution directory for the full license text.                 