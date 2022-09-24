# Internal Wireguard network, used for machine-to-machine communication

import subprocess

from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.operations import server

from util import get_file_path
from util.kdf import KeySource


def wg_pubkey(privkey: str):
	"""Derives the Wireguard public key for a given private key."""

	proc = subprocess.run(args=["wg", "pubkey"], input=privkey.encode(), stdout=subprocess.PIPE)
	proc.check_returncode()
	return proc.stdout.decode().strip()


@deploy("Intnet")
def apply():
	server.dnf.packages(
		name = "Install Wireguard userspace tools",
		packages = ["wireguard-tools"],
		_serial = host.data.dnf_serial,
	)

	config_file = server.files.template(
		name = "Install Wireguard config",
		src = get_file_path("wg-intnet.conf.j2"),
		dest = "/etc/wireguard/wg-intnet.conf",
		user = "root",
		group = "root",
		mode = "0400",

		# template data
		hostname = host.data.hostname,
		intnet_ip = host.data.intnet_ip,
		intnet_privkey = KeySource.derive_key_b64(host, "wireguard-internal-network-key-1", 32),
		intnet_peers = [{
			"name": peer.data.hostname,
			"intnet_ip": peer.data.intnet_ip,
			"public_addr": peer.data.ssh_hostname,
			"pubkey": wg_pubkey(KeySource.derive_key_b64(peer, "wireguard-internal-network-key-1", 32)),
		} for peer in inventory if peer != host],
	)

	server.systemd.service(
		name = "Activate Wireguard config",
		service = "wg-quick@wg-intnet.service",
		running = True,
		enabled = True,
		restarted = config_file.changed,
	)
