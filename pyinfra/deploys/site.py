# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from pyinfra import host

from roles import base, common, netdata, nginx


# Initial system preparation
base.apply()

# Common setup for all machines
common.apply()

# Netdata setup for all machines
netdata.apply()

# Nginx setup for flagship only
if host.data.primary_group == "flagship":
	nginx.apply()
