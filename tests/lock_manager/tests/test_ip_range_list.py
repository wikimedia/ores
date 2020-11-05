from ores.lock_manager.ip_range_list import IpRangeList


def test_matches_address():
    """
    Return a list of ip addresses.

    Args:
    """
    whitelist = [
        '127.0.0.1',
        '10.0.0.0/8',
    ]
    ip = '127.0.0.1'

    assert IpRangeList(whitelist).matches(ip)


def test_matches_range():
    """
    Return a list of whitelist.

    Args:
    """
    whitelist = [
        '127.0.0.1',
        '10.0.0.0/8',
    ]
    ip = '10.1.2.3'

    assert IpRangeList(whitelist).matches(ip)


def test_matches_ipv6():
    """
    Check if ipv6.

    Args:
    """
    whitelist = [
        '2001:db8::ff00:42:8329',
        '10.0.0.0/8',
    ]
    ip = '2001:db8::ff00:42:8329'

    assert IpRangeList(whitelist).matches(ip)


def test_matches_nonmatch():
    """
    Returns a list of ip addresses.

    Args:
    """
    whitelist = [
        '127.0.0.1',
        '10.0.0.0/8',
    ]
    ip = '4.3.2.1'

    assert not IpRangeList(whitelist).matches(ip)


def test_matches_mixed_type_safe():
    """
    Check if the whitelist matches the whitelelist.

    Args:
    """
    whitelist = [
        '2001:db8::ff00:42:8329',
        '10.0.0.0/8',
    ]
    ip = '4.3.2.1'

    assert not IpRangeList(whitelist).matches(ip)
