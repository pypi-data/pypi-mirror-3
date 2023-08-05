#!/usr/bin/env python2.6

from inqbus.ocf.generic import exits
from inqbus.ocf.generic import parameter
from inqbus.ocf.generic.agents.pidbaseagent import PIDBaseAgent
from subprocess import Popen


class OpenVPN(PIDBaseAgent):

	name = "openvpn.py"
	version = "1.0" 
	longdesc = "Resource agent for openvpn"
	shortdesc = "openvpn RA"

	def add_params(self):
		self.add_parameter(parameter.OCFString("ovpn_executable",
							longdesc="""Path to the executable""",
							shortdesc="executable",
							default = "/usr/sbin/openvpn") )
		self.add_parameter(parameter.OCFString("ovpn_name",
							longdesc="""Name of the OPENVPN channel""",
							shortdesc="VPN name",
							default = "flextra.inqbus.de") )
		self.add_parameter(parameter.OCFString("ovpn_dir",
							longdesc="""OpenVPN config dir""",
							shortdesc="OVPM dir",
							default = "/etc/openvpn") )
		
	def init(self):
		super(OpenVPN, self).init()
		self.config_file = '%s/%s.conf' % (self.params.ovpn_dir.value, self.params.ovpn_name.value)

	def get_pid_file(self):
		return '/var/run/openvpn.%s.pid' % self.params.ovpn_name.value
	
	def get_executable(self):
		return self.params.ovpn_executable.value
		
	def start_process(self):
		args =  [ self.executable,
				 '--daemon', 
				 '--writepid', self.pid_file, 
				 '--config', self.config_file, 
				 '--cd', self.params.ovpn_dir.value]
		proc = Popen(args)
		res = proc.communicate()
		if proc.returncode != 0 :
			raise exits.OCF_NOT_RUNNING()
		
		

if __name__ == "__main__":
	import sys
	OpenVPN().run(sys.argv)