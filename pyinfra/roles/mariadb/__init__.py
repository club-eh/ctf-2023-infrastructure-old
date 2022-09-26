# Install + configure MariaDB

from pyinfra import host
from pyinfra.api import deploy, operation
from pyinfra.facts.rpm import RpmPackages
from pyinfra.operations import files, server, mysql

from util import Flag, get_file_path, notify, KeySource


@operation
def install_mariadb_modular():
	pkgs = {
		"mariadb": "@mariadb:10.9/client",
		"mariadb-server": "@mariadb:10.9/server",
	}

	existing_pkgs = host.get_fact(RpmPackages).keys()

	missing_pkgs = set(pkgs.keys()).difference(existing_pkgs)
	if not len(missing_pkgs):
		host.noop("MariaDB server and client are both already installed")
		return

	yield from server.dnf.packages(packages=[pkgs[name] for name in missing_pkgs])


@deploy("MariaDB")
def apply():
	reload_systemd = Flag()
	restart_mariadb = Flag()

	notify(install_mariadb_modular(
		name = "Install MariaDB",
		_serial = host.data.dnf_serial,
	), reload_systemd)

	files.directory(
		name = "Create MariaDB data directory",
		path = "/persist/mariadb",
		user = "mysql",
		group = "mysql",
		mode = "0755",
	)

	notify(files.put(
		name = "Lockdown MariaDB service",
		src = get_file_path("service-lockdown.conf"),
		dest = "/etc/systemd/system/mariadb.service.d/lockdown.conf",
		user = "root",
		group = "root",
		mode = "644",
	), [reload_systemd, restart_mariadb])

	notify(files.put(
		name = "Configure MariaDB server",
		src = get_file_path("my.cnf.d/server.cnf"),
		dest = "/etc/my.cnf.d/mariadb-server.cnf",
		user = "root",
		group = "mysql",
		mode = "0640",
	), restart_mariadb)

	notify(files.put(
		name = "Configure MariaDB client",
		src = get_file_path("my.cnf.d/client.cnf"),
		dest = "/etc/my.cnf.d/client.cnf",
		user = "root",
		group = "mysql",
		mode = "0644",
	), restart_mariadb)

	# NOTE: this systemd interaction is flaky at best
	# Usually the service will be left "inactive (dead)" even though the server process is still running fine
	# Recovering the service requires manually killing the server process before restarting it
	server.systemd.service(
		name = "Activate MariaDB service",
		service = "mariadb.service",
		running = True,
		enabled = True,
		restarted = restart_mariadb,
		daemon_reload = reload_systemd,
	)

	# Create ctfd database
	# Not idempotent because the pyinfra operation depends on an accessible server during fact collection
	mysql.sql(
		name = "Create CTFd database",
		sql = "CREATE DATABASE IF NOT EXISTS ctfd;",
	)

	# Derive ctfd database password
	ctfd_db_pwd = "ctfd-key" + KeySource.derive_key(host, "mariadb-ctfd-database-key", 32).hex()

	# Create ctfd user with permissions on ctfd database
	# Unfortunately not idempotent
	mysql.sql(
		name = "Create CTFd user and grant privileges",
		sql = f"GRANT ALL PRIVILEGES ON ctfd.* TO 'ctfd'@'localhost' IDENTIFIED VIA ed25519 USING PASSWORD('{ctfd_db_pwd}');",
	)
