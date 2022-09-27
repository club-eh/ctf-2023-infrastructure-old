# Site-wide deployment (without stateless changes; ex. upgrading to the latest packages)

from pyinfra import host

from roles import base, common, ctfd, mariadb, netdata, nginx


# Initial system preparation
base.apply()

# Common setup for all machines
common.apply()

# Netdata setup for all machines
netdata.apply()

# Flagship-specific services
if host.data.primary_group == "flagship":
	nginx.apply()
	mariadb.apply()
	ctfd.apply()
