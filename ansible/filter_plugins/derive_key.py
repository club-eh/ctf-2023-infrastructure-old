from base64 import b64decode, b64encode
import hashlib
import hmac
import math
from typing import Literal
import uuid

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError


class HKDF:
	"""Loose implementation of HKDF, with some tweaks.

	Based on code from https://en.wikipedia.org/wiki/HKDF#Example:_Python_implementation
	"""

	# use not-RFC-compliant hash function, because SHA-256 is boring
	hash_func = hashlib.sha3_512
	hash_len = 64

	@classmethod
	def _hmac_func(cls, key: bytes, msg: bytes) -> bytes:
		return hmac.new(key, msg, cls.hash_func).digest()

	@classmethod
	def derive_key(cls, root_km: bytes, label: bytes, length: int) -> bytearray:
		# use RFC5869-compliant salt
		salt = bytes(length)

		prk = cls._hmac_func(salt, root_km)

		t = bytes()
		output = bytearray()

		for i in range(math.ceil(length / cls.hash_len)):
			t = cls._hmac_func(prk, t + label + bytes([i + 1]))
			output.extend(t)

		return output[:length]


key_formats = {"hex", "base64", "uuid", "uuidv4"}

# A valid key format.
# "uuid" is an alias for UUIDv4
KeyFormat = Literal["hex", "base64", "uuid", "uuidv4"]


def derive_key(root_key: bytes | str, label: str, key_format: KeyFormat = "base64", key_len: int = 32):
	if isinstance(root_key, bytes):
		actual_rk = root_key
	elif isinstance(root_key, str):
		try:
			actual_rk = b64decode(root_key)
		except ValueError as e:
			raise AnsibleFilterError(f"Failed to parse base64 string: {e}")
	else:
		raise AnsibleFilterTypeError(f"Root key must be raw bytes or a base64-encoded string; instead we got: {type(root_key)}")

	if not isinstance(label, str):
		raise AnsibleFilterTypeError(f"Label must be a string; instead we got: {type(label)}")

	if not key_format in key_formats:
		raise AnsibleFilterTypeError(f"Invalid key_format: {key_format}")

	if key_len < 1:
		raise AnsibleFilterError(f"Invalid key_len (must be a positive integer): {key_len}")

	if key_format in {"uuid", "uuidv4"}:
		key_len = 16

	# derive raw output key
	output_key = HKDF.derive_key(actual_rk, label.encode(), key_len)

	# convert to output format and return
	if key_format == "hex":
		return output_key.hex()
	elif key_format == "base64":
		return b64encode(output_key).decode()
	elif key_format == "uuid" or key_format == "uuidv4":
		return str(uuid.UUID(version=4, bytes=bytes(output_key)))


class FilterModule:
	def filters(self):
		return {
			"derive_key": derive_key,
		}
