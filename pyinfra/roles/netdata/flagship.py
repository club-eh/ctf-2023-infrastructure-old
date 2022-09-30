# Flagship-specific Netdata setup

from pyinfra import host
from pyinfra.api import operation
from pyinfra.operations import files

from util import KeySource, get_file_path


CONFIG_FILE_PERMS = dict(
	user = "root",
	group = "netdata",
	mode = "0640",
)


@operation
def configure_flagship():
	"""Install flagship-specific Netdata configuration files."""

	# Configure Redis collector
	yield from files.template(
		src = get_file_path("flagship/go.d/redis.conf.j2"),
		dest = "/etc/netdata/go.d/redis.conf",
		**CONFIG_FILE_PERMS,
		# template data
		redis_pwd = KeySource.derive_key(host, "redis-user-pwd-netdata", 32).hex(),
	)
