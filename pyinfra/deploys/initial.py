# Initial deploy - prepares the system for later deployments

from pyinfra import host

from roles import base, ctfd


# Initial system preparation
base.apply()


# Pre-init steps (aka workaround for pyinfra limitations)
if host.data.primary_group == "flagship":
	ctfd.apply_preinit()
