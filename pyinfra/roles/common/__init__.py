# Common system-wide changes for all machines

from pyinfra.api import deploy

from . import harden_ssh, harden_system


@deploy("Common")
def apply():
	harden_system.apply()
	harden_ssh.apply()

# TODO: enable and configure FirewallD
