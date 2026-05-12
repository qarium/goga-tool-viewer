"""Find a free TCP port in a given range."""

import random
import socket


def find_free_port(min_port: int, max_port: int) -> int:
    """Return a free TCP port in [min_port, max_port].

    Tries ports in random order. Raises OSError if no free port is found.
    """
    ports = list(range(min_port, max_port + 1))
    random.shuffle(ports)
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("", port))
            s.close()
            return port
        except OSError:
            s.close()
    raise OSError(f"No free port found in range {min_port}-{max_port}")
