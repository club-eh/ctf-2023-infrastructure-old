"""Utilities for computing file paths."""

import inspect
from pathlib import Path


# Absolute path of the base roles/ subdirectory
_ROLES_DIRECTORY_PATH = (Path(__file__).parents[1] / "roles").resolve()


def get_role_path() -> Path:
	"""Returns the current role's base directory path.
	
	Example:
	```py
	# roles/my_role/sub_module.py:
	>>> get_role_path()
	Path("roles/my_role")
	```
	"""

	# retrieve current stack frame
	frame = inspect.currentframe()
	if frame is None:
		raise Exception("Python interpreter does not support inspect.currentframe()")

	# switch to caller's frame
	frame = frame.f_back

	# walk up the call stack until we find a submodule of roles
	while frame is not None:
		module_path_str: str | None = frame.f_globals.get("__file__")
		if module_path_str is not None:
			module_path = Path(module_path_str)
			try:
				local_path = module_path.relative_to(_ROLES_DIRECTORY_PATH)
			except ValueError:
				pass
			else:
				# found a module under roles/
				role_name = local_path.parts[0]
				return _ROLES_DIRECTORY_PATH / role_name

		# couldn't find a match, move up the call stack and try again
		frame = frame.f_back

	# reached end of call stack without finding a suitable 
	raise Exception("Unable to determine role directory: current frame is None")

def get_file_path(filename: str) -> Path:
	"""Returns the filepath for a given local file resource (under the current role).

	Convenience wrapper around `get_role_path()`.
	"""

	return get_role_path() / "files" / filename
