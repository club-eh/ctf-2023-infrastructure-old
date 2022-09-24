# Common system-wide changes for all machines

from pyinfra.api import deploy

from . import configure_ssh, harden_system


@deploy("Common")
def apply():
	harden_system.apply()
	configure_ssh.apply()

# TODO: enable and configure FirewallD
