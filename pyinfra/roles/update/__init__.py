# System updates (stateless operations that are not idempotent)

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import server


@deploy("Updates")
def apply():
	server.shell(
		name="Update system packages",
		commands="dnf upgrade --assumeyes",
		_serial=host.data.dnf_serial,
	)

	server.shell(
		name="Remove unused dependencies",
		commands="dnf autoremove --assumeyes",
		_serial=host.data.dnf_serial,
	)
