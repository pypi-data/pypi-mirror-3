
from __future__ import print_function

import sys, os
import traceback
from xml.etree import ElementTree

from inqbus.ocf.generic import exits
from inqbus.ocf.generic import parameter
from inqbus.ocf.generic import handlers

class Agent(object):
    """
    API-Class: To be derived from the actual agent classes.
    Each child have to implement at least the add_params and the init function.
    """
    name = "agent.py"
    version = "1.0" # Do not change!
    longdesc = "Resource agent"
    shortdesc = "RA"

    def __init__(self):
        """
        Create the paramter and the action storage. Populate the actions with
        the default handlers.
        """

        # Container for the parameters
        self.params = parameter.Parameters()
        # Container for the handlers
        self.handlers = handlers.Handlers()
        # set the default handlers
        self.handlers[handlers.ACTION_METADATA] = handlers.Handler(Agent.stdout_meta_data, 10)
        self.handlers[handlers.ACTION_VALIDATE_ALL] = handlers.Handler(Agent.validate_all, 10)

    def config(self):
        """
        Here Pacemaker parameters and action handlers are added to the agent. 
        Has to be implemented from inheriting classes.
        
        Is called 
        """
        raise NotImplementedError("To use Agent you have to implement the config() method")

    def init(self):
        """
        The initialization of the member variables namely the ones derived from 
        the Pacemaker parameters is done here. 
        Has to be implemented from inheriting classes.
        
        Is called after config() was called and the parameter values from the 
        Environment have been read and verified. 
        """
        raise NotImplementedError("To use Agent you have to implement a init() routine ")

    def get_commandline_action(self, argv):
        """
        Check for the right format of the sys.argv input and return the command 
        line action. E.g. start, stop, status.
        
        There has to be exactly one commandline argument requiring two arguments
        in the sys.argv argument vector.
        """
        if isinstance(argv, str):
            # Input is a single string, accept it as the command argument
            return argv
        if not isinstance(argv, list) or len(argv) != 2 :
            # argument is nor vector or vector length does not fit -> error 
            raise exits.OCF_ERR_UNIMPLEMENTED(self.usage())
        else:
            # Accept second commandline string as argument 
            return argv[1]

    def get_handler_for_commandline_action(self, action):
        """
        Check if the requested action is a valid OCF action
        and if the action is implemented.
        """
        if action not in self.handlers:
            raise exits.OCF_ERR_UNIMPLEMENTED(self.usage())
        return self.handlers[action]

    def run(self, argv):
        """
        Main procedure triggered from pacemaker or the command line via sys.argv.
        """
        try :

            # Configure the agent (parameter and handler registration)
            self.config()

            # Fetch the desired action from the argv
            action = self.get_commandline_action(argv)
            # Retrieve the handler for the action
            handler = self.get_handler_for_commandline_action(action)

            # Check if the action is METADATA. On this action ocf-tester does not
            # initialize the environment. So read_env() and init() that rely 
            # on the enviroment will fail.  
            if handler.action not in [handlers.ACTION_METADATA] :
                # Fill the parameter with the pacemaker values from the os.environment
                self.read_env()
                # Give the inheriting class a chance to derive member variables from 
                # the parameter values
                self.init()

            # Execute the handler
            handler.handler(self)

        # Let all OCF-Error-Exits pass
        except exits.OcfError:
            raise
        # Catch all other exceptions and log a traceback.
        except Exception:
            # Send to stderr, since this is probably a script problem
            traceback.print_exc(file=sys.stderr)
        return True


    def read_env(self):
        """
        Read the Pacemaker Parameters from the environment.
        """
        # Save the environment to prevent race conditions
        env = os.environ
        # read the instance name from OCF_RESOURCE_INSTANCE
        try:
            self.instance_name = env['OCF_RESOURCE_INSTANCE']
        except KeyError:
            self.instance_name = self.name

        try:
            desired_version = '.'.join([env['OCF_RA_VERSION_MAJOR'],
                                        env['OCF_RA_VERSION_MINOR']])
        except KeyError:
            desired_version = '1.0'
        if not self.version == desired_version:
            exits.OCF_ERR_CONFIGURED('Version mismatch of agent and Pacemaker')

        # Check all parameters
        for parameter in list(self.params.values()):
            # Is the parameter not available
            if parameter.envname not in env:
                # and required
                if parameter.required:
                    # Then complain
                    err_str = "Required parameter \"%s\" missing" % parameter.name
                    raise exits.OCF_ERR_CONFIGURED(err_str)
                else :
                    # if not then use the default value
                    # TODO : Default value may not available!
                    parameter.value = parameter.default
            else :
                parameter.value = env[parameter.envname]

            # The parameter is available from the environment and validate it
            try:
                parameter.validate(self, parameter)
            except ValueError as e:
                err_str = "Invalid value for parameter %s: %s" % (parameter.name, e.message)
                raise exits.OCF_ERR_CONFIGURED(err_str)

    def usage(self):
        """
        Print usage message
        """
        return "Usage: %s <%s>\n" % (self.name, "|".join(self.handlers.keys()))

    def meta_data(self):
        """
        Derive a pacemaker conform xml description of the plugins services
        """
        eResourceAgent = ElementTree.Element("resource-agent", {"name": self.name, "version": self.version})
        ElementTree.SubElement(eResourceAgent, "version").text = "1.0"

        ElementTree.SubElement(eResourceAgent, "longdesc", {"lang": "en"}).text = self.longdesc
        ElementTree.SubElement(eResourceAgent, "shortdesc", {"lang": "en"}).text = self.shortdesc

        eParameters = ElementTree.SubElement(eResourceAgent, "parameters")
        for p in (p.getelement() for p in self.params.values()):
            eParameters.append(p)

        eActions = ElementTree.SubElement(eResourceAgent, "actions")
        for handler in list(self.handlers.values()) :
            p = { }
            p["name"] = handler.action
            p['timeout'] = str(handler.timeout)
            eActions.append(ElementTree.Element("action", p))

        return eResourceAgent

    def stdout_meta_data(self):
        xml_meta_data = self.meta_data()
        sys.stdout.write("""<?xml version="1.0"?>
<!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
""")
        ElementTree.ElementTree(xml_meta_data).write(sys.stdout)
        sys.stdout.write("\n")

    def validate_all(self):
        """
        Validate the values of the Parameters from the environment.
        If a custom validator handler for the OCF-Agent is registered then 
        execute it.   
        """
        self.read_env()
        if 'validate' in self.handlers:
            self.handlers['validate']()
