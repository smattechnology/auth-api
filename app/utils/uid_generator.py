import random
import string


def get_random_alphabet():
    """Return a random letter, either uppercase or lowercase."""
    return random.choice(string.ascii_letters)


def get_random_integer():
    """Return a random single-digit integer between 0 and 9."""
    return random.randint(0, 9)


def get_random_boolean():
    """Return a random boolean value (True or False)."""
    return random.choice([True, False])


def d_uid(prefix: str | None = None) -> str:
    uid = prefix or ""
    for _ in range(10):
        if get_random_boolean():
            uid += get_random_alphabet()
        else:
            uid += str(get_random_integer())
    return uid.upper()


# Expose only get_uid
__all__ = ["d_uid"]