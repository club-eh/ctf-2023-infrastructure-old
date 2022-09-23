# Static inventory file for local test environments using Vagrant.

from ipaddress import IPv4Address


MACHINE_PREFIX = "ctf-"
CHALLENGE_MACHINES = 1


def machine(name: str, conn_address: str):
	"""DRY wrapper to generate host entries.

	name: Name of the machine.
	conn_address: The actual IP / hostname that can be used to connect to the machine via SSH.
	"""

	machine_name = MACHINE_PREFIX + name

	return (machine_name, {
		"ssh_hostname": conn_address,
		"hostname": machine_name,
		"domain": machine_name + ".localctf",
		"vagrant_static_ip": conn_address,
	})


flagship = [machine("flagship", "192.168.61.10")]

challenges = [machine(
	f"challenges-{n}",
	(IPv4Address("192.168.61.10") + n).compressed,
) for n in range(1, CHALLENGE_MACHINES + 1)]

local = vagrant = [*flagship, *challenges]
