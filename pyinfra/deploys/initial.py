# Initial deploy - prepares the system for later deployments

from pyinfra import config

from roles import base


# Run everything with sudo by default
config.SUDO = True


# Initial system preparation
base.apply()
