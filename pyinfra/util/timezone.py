from pyinfra import host
from pyinfra.api import FactBase, operation
from pyinfra.facts.server import Which


class Timezone(FactBase):
	"""
	Returns the current timezone of the server.
	"""

	# Systemd-only
	#command = "timedatectl show -p Timezone --value"

	# Should be portable across most Linux distributions
	command = "readlink -nm /etc/localtime | sed 's|^/usr/share/zoneinfo/||'"


@operation
def timezone(timezone: str):
	"""
	Set the system timezone using `timedatectl` or `/etc/localtime`.

	+ timezone: the TZ database name of the timezone that should be set

	This operation will attempt to set the system timezone using `timedatectl` if available.  
	Otherwise, it will fallback to linking `/etc/localtime` to `/usr/share/zoneinfo/{timezone}`.
	"""

	current_timezone = host.get_fact(Timezone)

	if current_timezone == timezone:
		host.noop("timezone is set")
		return

	if host.get_fact(Which, command="timedatectl"):
		yield f"timedatectl set-timezone {timezone}"
	else:
		yield f"ln -sf /usr/share/zoneinfo/{timezone} /etc/localtime"

	host.create_fact(Timezone, data=timezone)
