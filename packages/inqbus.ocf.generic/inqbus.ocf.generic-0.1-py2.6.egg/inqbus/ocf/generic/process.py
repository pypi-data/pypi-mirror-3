#!/usr/bin/env python

from os import kill, waitpid, WNOHANG
from signal import SIGTERM, SIGINT, SIGHUP, SIGKILL
from subprocess import Popen
from time import sleep
from os.path import exists

from ocf import resourceagent
from ocf import errors

agent = resourceagent.ResourceAgent("generic_pid", "1.0", "A generic agent for processes utilizing a PID", "Generic PID RA")
agent.add_parameter("ovpn_executable",
	longdesc="""Path to the executable""",
	shortdesc="executable",
	datatype=resourceagent.STRING)
agent.add_parameter("ovpn_name",
	longdesc="""Name of the OPENVPN channel""",
	shortdesc="VPN name",
	datatype=resourceagent.STRING)
agent.add_parameter("ovpn_dir",
	longdesc="""OpenVPN config dir""",
	shortdesc="OVPM dir",
	datatype=resourceagent.STRING,
	default = "/etc/openvpn")

def get_pid(env):
	pid_file_path = '/var/run/openvpn.%s.pid' % env.params.ovpn_name
	if exists(pid_file_path):
		try :
			pid_file = open(pid_file_path)
		except :
			raise errors.OCF_ERR_PERM('cannot open pid file: %s' % pid_file_path)
		try :
			pid_str = pid_file.read()
		except :
			raise errors.OCF_ERR_PERM('cannot read pid file : %s' % pid_file_path)
		try :
			pid = int(pid_str)
		except :	
			raise errors.OCF_ERR_PERM('no pid in file : %s'  % pid_file_path)
		return pid
	else :
		return None 

def kill(pid, signal=0):
	"""sends a signal to a process
    returns True if the pid is dead
    with no signal argument, sends no signal"""
	try: 
		return kill(pid, signal)
	except OSError, e:
		#process is dead
		if e.errno == 3: 
			return True
		#no permissions
		elif e.errno == 1: 
			return False
		else: 
			raise

def dead(pid):
	if kill(pid): return True

	#maybe the pid is a zombie that needs us to wait4 it
	try: 
		dead = waitpid(pid, WNOHANG)[0]
	except OSError, e:
		#pid is not a child
		if e.errno == 10: 
			return False
		else: raise
	return dead

#def kill(pid, sig=0): pass #DEBUG: test hang condition

def goodkill(pid, interval=1, hung=2):
	"""let process die gracefully, gradually send harsher signals if necessary"""
	
	for signal in [SIGTERM, SIGINT, SIGHUP]:
		if kill(pid, signal): 
			return True
		if dead(pid): 
			return True
		sleep(interval)
		
	i = 0
	while True:
		#infinite-loop protection
		if i < hung:
			i += 1	
		else:
			return False
		if kill(pid, SIGKILL): 
			return True
		if dead(pid): 
			return True
		sleep(interval) 

def start_process(env):
	executable = env.params.ovpn_executable
	config_file = '%s/%s.conf' % (env.params.ovpn_dir, env.params.ovpn_name)
	pid_file = '/var/run/openvpn.%s.pid' % env.params.ovpn_name
	args =  [executable, '--writepid', pid_file, '--config', config_file, '--cd', env.params.ovpn_dir]
	Popen(args)

def stop_process(pid, env):
	if not dead(pid):
		goodkill(pid)
	else :
		raise resourceagent.OCF_NOT_RUNNING()

def do_start(env):
	if not get_pid(env) :
		start_process(env)

def do_stop(env):
	if get_pid(env) :
		stop_process(env)
	else :
		raise resourceagent.OCF_NOT_RUNNING()
		
def do_monitor(env):
	pid = get_pid(env)
	if not pid or dead(pid):
		raise resourceagent.OCF_NOT_RUNNING()

agent.add_action("start", {"timeout": "20s"}, do_start)
agent.add_action("stop", {"timeout": "20s"}, do_stop)
agent.add_action("monitor", {"timeout": "20s"}, do_monitor)

if __name__ == "__main__":
	import sys
	agent.run(sys.argv)