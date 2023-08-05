from os import kill, waitpid, WNOHANG, remove
from signal import SIGTERM, SIGINT, SIGHUP, SIGKILL
from time import sleep
from os.path import exists

from inqbus.ocf.generic.agent import Agent
from inqbus.ocf.generic import exits

class PIDBaseAgent(Agent):

    def init(self):
        self.pid_file = self.get_pid_file()
        self.executable = self.get_executable()
        self.get_pid()

    def get_pid_file(self):
        raise NotImplementedError( "To use PIDAgent you have to implement a get_pid_file() routine that returns the PID-File")

    def get_executable(self):
        raise NotImplementedError( "To use PIDAgent you have to implement a get_executable() routine that return the executable location")

    def get_pid(self):
        if exists(self.pid_file):
            try :
                pid_file = open(self.pid_file)
            except :
                raise exits.OCF_ERR_PERM('cannot open pid file: %s' % self.pid_file)
            try :
                pid_str = pid_file.read()
            except :
                raise exits.OCF_ERR_PERM('cannot read pid file : %s' % self.pid_file)
            try :
                self.pid = int(pid_str)
            except :    
                raise exits.OCF_ERR_PERM('no pid in file : %s'  % self.pid_file)
        else :
            self.pid =    None 
        return self.pid

    def rm_pid_file(self):
        if exists(self.pid_file):
            remove( self.pid_file )
    
    def kill_pid(self, signal=0):
        """sends a signal to a process
        returns True if the pid is dead
        with no signal argument, sends no signal"""
        try: 
            return kill(self.pid, signal)
        except OSError as e:
            #process is dead
            if e.errno == 3: 
                return True
            #no permissions
            elif e.errno == 1: 
                return False
            else: 
                raise
    
    def dead(self):
        if self.kill_pid(): return True
    
        #maybe the pid is a zombie that needs us to wait4 it
        try: 
            dead = waitpid(self.pid, WNOHANG)[0]
        except OSError as e:
            #pid is not a child
            if e.errno == 10: 
                return False
            else: raise
        return dead
    
    def running(self):
        return not self.dead()
    
    #def kill(pid, sig=0): pass #DEBUG: test hang condition
    
    def goodkill(self, interval=1, hung=2):
        """let process die gracefully, gradually send harsher signals if necessary"""
        
        for signal in [SIGTERM, SIGINT, SIGHUP]:
            if self.kill_pid(signal): 
                return True
            if self.dead(): 
                return True
            sleep(interval)
            
        i = 0
        while True:
            #infinite-loop protection
            if i < hung:
                i += 1    
            else:
                return False
            if self.kill_pid(SIGKILL): 
                return True
            if self.dead(): 
                return True
            sleep(interval) 

    def wait_pid( self, interval=1  ):
        while True:
            self.get_pid()
            if self.pid and self.running(): 
                return True
            sleep(interval) 
                   
    def stop_process(self):
        return self.goodkill()
    
    def do_start(self):
        if not self.pid or self.dead() :
            self.start_process()            
            if not self.wait_pid():
                raise exits.OCF_NOT_RUNNING()
    
    def do_stop(self):
        if self.pid :
            if not self.dead() :
                if self.stop_process() :
                    self.rm_pid_file()
            else :
                self.rm_pid_file()
            
    def do_monitor(self):
#        import pdb; pdb.set_trace()
        if not self.pid or self.dead():
            raise exits.OCF_NOT_RUNNING()
        