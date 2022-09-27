# Install + configure CTFd

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, git, pip, server

from util import Flag, KeySource, get_file_path, notify


CTFD_GIT_REPO = "https://git.sb418.net/sudoBash418/CTFd.git"
CTFD_GIT_BRANCH = "deploy"
CTFD_ACCOUNT_ID = 600  # hardcode UID/GID to avoid issues with /persist


@deploy("CTFd pre-init")
def apply_preinit():
	"""Pre-init operations that need to be completed before the main deploy."""

	server.group(
		name = "Create CTFd group",
		group = "ctfd",
		system = True,
		gid = CTFD_ACCOUNT_ID,
	)

	server.user(
		name = "Create CTFd user",
		user = "ctfd",
		system = True,
		uid = CTFD_ACCOUNT_ID,
		home = "/opt/ctfd",
		create_home = True,
		comment = "Service user for the CTFd application",
	)



@deploy("CTFd")
def apply():
	reload_systemd = Flag()
	restart_ctfd = Flag()


	files.directory(
		name = "Create persistent directory",
		path = "/persist/ctfd",
		user = "ctfd",
		group = "ctfd",
		mode = "750",
	)

	server.dnf.packages(
		name = "Install system dependencies",
		packages = [
			"python3-pip",
			"python3-wheel",
		],
		_serial = host.data.dnf_serial,
	)

	notify(git.repo(
		name = "Install CTFd from git",
		src = CTFD_GIT_REPO,
		branch = CTFD_GIT_BRANCH,
		dest = "/opt/ctfd/app",
		pull = True,
		update_submodules = True,
		user = "ctfd",
		group = "ctfd",
		_sudo_user = "ctfd",  # git does weird things if we're not running as the correct user
	), restart_ctfd)

	notify(pip.packages(
		name = "Install Python dependencies",
		requirements = "/opt/ctfd/app/requirements.txt",
		virtualenv = "/opt/ctfd/venv",
		virtualenv_kwargs = dict(
			python = "python3",
			venv = True,  # use stdlib module
		),
		_sudo_user = "ctfd",  # install python dependencies as user
	), restart_ctfd)


	notify(files.put(
		name = "Install CTFd service file",
		src = get_file_path("ctfd.service"),
		dest = "/usr/local/lib/systemd/system/ctfd.service",
		user = "root",
		group = "root",
		mode = "644",
	), [reload_systemd, restart_ctfd])

	notify(files.put(
		name = "Install CTFd socket file",
		src = get_file_path("ctfd.socket"),
		dest = "/usr/local/lib/systemd/system/ctfd.socket",
		user = "root",
		group = "root",
		mode = "644",
	), [reload_systemd, restart_ctfd])

	notify(files.put(
		name = "Install CTFd wrapper script",
		src = get_file_path("run-ctfd.sh"),
		dest = "/opt/ctfd/run-ctfd.sh",
		user = "root",
		group = "ctfd",
		mode = "750",
	), restart_ctfd)

	notify(files.template(
		name = "Install CTFd config file",
		src = get_file_path("ctfd.env.j2"),
		dest = "/opt/ctfd/ctfd.env",
		user = "root",
		group = "ctfd",
		mode = "640",
		# template args
		ctfd_secret_key = KeySource.derive_key_b64(host, "ctfd-secret-key", 64),
		ctfd_mariadb_pwd = KeySource.derive_key(host, "mariadb-ctfd-database-key", 32).hex(),
	), restart_ctfd)


	server.systemd.service(
		name = "Activate CTFd service",
		service = "ctfd.service",
		running = True,
		enabled = True,
		restarted = restart_ctfd,
		daemon_reload = reload_systemd,
	)
