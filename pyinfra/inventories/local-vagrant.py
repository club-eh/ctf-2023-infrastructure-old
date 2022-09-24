# Static inventory file for local test environments using Vagrant.

from ipaddress import IPv4Address


MACHINE_PREFIX = "ctf-"
CHALLENGE_MACHINES = 1


def machine(name: str, public_ip: IPv4Address, intnet_ip: IPv4Address, **kwargs):
	"""DRY wrapper to generate host entries.

	name: Name of the machine.
	public_ip: The "public"-facing IP / hostname (can normally be used to connect to the machine via SSH).
	intnet_addr: The internal IP for the Wireguard internal network.
	"""

	machine_name = MACHINE_PREFIX + name

	return (machine_name, {
		"ssh_hostname": public_ip.compressed,
		"hostname": machine_name,
		"domain": machine_name + ".localctf",
		"vagrant_static_ip": public_ip.compressed,
		"intnet_ip": intnet_ip.compressed,
		**kwargs,
	})


flagship = [machine(
	"flagship",
	public_ip=IPv4Address("192.168.61.10"),
	intnet_ip=IPv4Address("192.168.50.1"),
)]

challenges = [machine(
	f"challenges-{n+1}",
	public_ip=IPv4Address("192.168.61.11") + n,
	intnet_ip=IPv4Address("192.168.50.16") + n,
) for n in range(CHALLENGE_MACHINES)]

local = vagrant = [*flagship, *challenges]
