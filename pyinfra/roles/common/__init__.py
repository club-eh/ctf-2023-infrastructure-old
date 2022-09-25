# Common system-wide changes for all machines

from pyinfra.api import deploy

from . import configure_ssh, extra_packages, harden_system, setup_intnet


@deploy("Common")
def apply():
	harden_system.apply()
	configure_ssh.apply()

	extra_packages.apply()

	setup_intnet.apply()

# TODO: enable and configure FirewallD
