# Dynamic inventory file for bootstrapping a Vagrant local test environment.

import os
from ipaddress import IPv4Address

from pyinfra.connectors import vagrant


MACHINE_PREFIX = "ctf-"
CHALLENGE_MACHINES = 1
VAGRANT_DIR = "../vagrant"


# get connection info from Vagrant
_prev_dir = os.path.realpath(os.curdir)
os.chdir(VAGRANT_DIR)
# convert (name, data, group_names) -> {name: data}
vagrant_data = { entry[0] : entry[1] for entry in vagrant.make_names_data() }
os.chdir(_prev_dir)
del _prev_dir


def machine(name: str, static_address: str):
	"""DRY wrapper to generate host entries.

	name: Name of the machine (ex. flagship).
	static_address: The internal static IP the machine should be assigned.
	"""

	machine_name = MACHINE_PREFIX + name

	vdata = vagrant_data[f"@vagrant/{machine_name}"]

	return (machine_name, {
		**vdata,
		"hostname": machine_name,
		"domain": machine_name + ".localctf",
		"vagrant_static_ip": static_address,
	})


flagship = [machine("flagship", "192.168.61.10")]

challenges = [machine(
	f"challenges-{n}",
	(IPv4Address("192.168.61.10") + n).compressed,
) for n in range(1, CHALLENGE_MACHINES + 1)]

local = vagrant = [*flagship, *challenges]
