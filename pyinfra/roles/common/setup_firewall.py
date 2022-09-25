# Install + configure nftables firewall

from io import StringIO

from pyinfra import host
from pyinfra.api import StringCommand, deploy, operation
from pyinfra.facts.rpm import RpmPackages
from pyinfra.operations import server

from util import Reactor, get_file_path, notify


@operation
def install_nftables():
	"""Custom operation for sorting out the nftables-firewalld dependency issue.

	Note: this mess is required because nftables is a dependency of firewalld, and pyinfra/rpm does not track or set install purpose.
	"""

	existing_pkgs = set(host.get_fact(RpmPackages).keys())

	if "firewalld" not in existing_pkgs and "nftables" in existing_pkgs:
		host.noop("nftables is installed and firewalld is not")
		return

	if "firewalld" in existing_pkgs:
		# mark nftables as explicitly installed (or install it if it's somehow missing)
		yield StringCommand("dnf mark install nftables || dnf install -y nftables")
		# uninstall firewalld
		yield from server.dnf.packages(packages=["firewalld"], present=False)
	else:
		# install nftables
		yield from server.dnf.packages(packages=["nftables"], present=True)


@deploy("Setup firewall")
def apply():
	reload_systemd = Reactor()
	reload_firewall = Reactor()

	# swap firewalld for nftables
	notify(install_nftables(
		name="Uninstall firewalld and install nftables",
		_serial=host.data.dnf_serial,
	), reload_systemd)

	# install config files
	notify(server.files.put(
		name = "Install main firewall config",
		src = get_file_path("nftables/main.nft"),
		dest = "/etc/nftables/main.nft",
		user = "root",
		group = "root",
		mode = "0600",
	), reload_firewall)
	notify(server.files.template(
		name = "Install machine-specific firewall config",
		src = get_file_path(f"nftables/{host.data.primary_group}.nft.j2"),
		dest = "/etc/nftables/machine.nft",
		user = "root",
		group = "root",
		mode = "0600",
		# restrict access to nginx in staging environment
		allow_public = host.data.env_name != "staging",
		trusted_ips = getattr(host.data, "trusted_ips", None),
	), reload_firewall)
	notify(server.files.put(
		name = "Configure sysconfig to use our firewall rules",
		src = StringIO('include "/etc/nftables/main.nft";'),
		dest = "/etc/sysconfig/nftables.conf",
		user = "root",
		group = "root",
		mode = "0600",
	), reload_firewall)

	# apply firewall rules
	server.systemd.service(
		name = "Activate nftables rules",
		service = "nftables.service",
		running = True,
		enabled = True,
		reloaded = reload_firewall.triggered,
		daemon_reload = reload_systemd.triggered,
	)
