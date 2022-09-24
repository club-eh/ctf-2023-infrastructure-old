# Install some useful QoL packages

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import dnf


@deploy("Extra packages")
def apply():
	dnf.packages(
		name = "Install extra QoL packages",
		packages = [
			"bash-completion",  # enables shell completion
			"git",
			"nano",  # simple text editor
			"micro",  # nano but better
			"ripgrep",  # grep but better
			"btop",  # htop but better
			"ldns-utils",  # includes drill for debugging DNS
		],
		_serial = host.data.dnf_serial,
	)
