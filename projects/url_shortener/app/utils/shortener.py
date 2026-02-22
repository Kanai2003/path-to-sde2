"""URL shortening utilities."""
import hashlib
import string

BASE62 = string.ascii_uppercase + string.ascii_lowercase + string.digits


def _base62_encode(num: int) -> str:
    """
    Convert integer to Base62 string.

    Args:
        num: Integer to encode

    Returns:
        Base62 encoded string
    """
    if num == 0:
        return BASE62[0]

    arr: list[str] = []
    base = len(BASE62)

    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62[rem])

    arr.reverse()
    return "".join(arr)


def generate_short_code(original_url: str, length: int = 6, salt: int = 0) -> str:
    """
    Generate a short code from the original URL.

    Args:
        original_url: The URL to generate a code for
        length: Length of the short code (default: 6)
        salt: Salt value for collision handling (default: 0)

    Returns:
        Base62 encoded short code
    """
    # Add salt for collision handling
    data = f"{original_url}{salt}" if salt else original_url

    # SHA256 hash
    hash_object = hashlib.sha256(data.encode())
    hex_digest = hash_object.hexdigest()

    # Convert hex → int
    num = int(hex_digest, 16)

    # Convert to Base62
    base62_str = _base62_encode(num)

    # Take first N chars
    return base62_str[:length]
