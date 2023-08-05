from pidbaseagent import PIDBaseAgent
from inqbus.ocf.generic import parameter

class PIDAgent(PIDBaseAgent):
    
    def init(self):
        super(PIDAgent, self).init()
        
    def add_params(self):
        self.add_parameter(parameter.OCFString("executable", 
                            longdesc="""Path to the executable""",
                            shortdesc="executable",
                            required= True) )
        self.add_parameter(parameter.OCFString( "pid_file",
                            longdesc="""Path to the pid file""",
                            shortdesc="executable",
                            required= True) )
    
    def get_pid_file(self):
        return self.params.pid_file.value
    
    def get_executable(self):
        return self.params.executable.value

if __name__ == "__main__":
    import sys
    PIDAgent().run(sys.argv)