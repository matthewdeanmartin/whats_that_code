"""
Builds fail when they're not on VPN or can't reach remote servers
"""
import ifaddr
import requests


def check_public_ip(ipify: str = "https://api64.ipify.org/") -> str:
    """
    Try to get the elastic IP for this machine
    """
    # BUG: When this fails, it doesn't fail fast.

    # pylint: disable=bare-except,broad-except
    # noinspection PyBroadException
    try:
        # https://api.ipify.org # fails on VPN.
        # pylint: disable=invalid-name
        ip = requests.get(ipify).text
        return ip
    except BaseException:  # noqa
        return ""


def is_known_network(prefix: str) -> bool:
    """Are we on a known network"""

    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        # pylint: disable=invalid-name
        for ip in adapter.ips:
            if str(ip.ip).startswith(prefix):
                return True
    return False
