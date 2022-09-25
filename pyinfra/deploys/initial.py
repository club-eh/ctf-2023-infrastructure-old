# Initial deploy - prepares the system for later deployments

from pyinfra.operations import server

from roles import base


# Initial system preparation
base.apply()

# Ensure root login is disabled
server.shell("passwd -l root")
