# Site-wide updates (with stateless changes; ex. upgrading to the latest packages)

from pyinfra import config

from roles import update


# Run everything with sudo by default
config.SUDO = True


update.apply()
