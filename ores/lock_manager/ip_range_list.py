import ipaddress


class IpRangeList:
    def __init__(self, whitelist):
        """
        Initialize the whitelist.

        Args:
            self: (todo): write your description
            whitelist: (str): write your description
        """
        self.whitelist = whitelist

    def matches(self, ip):
        """
        Returns true if the given ip matches the given ip.

        Args:
            self: (todo): write your description
            ip: (str): write your description
        """
        search_ip = ipaddress.ip_address(ip)
        for pattern_ip in self.whitelist:
            ip_range = ipaddress.ip_network(pattern_ip)
            try:
                if search_ip in ip_range:
                    return True
            except TypeError:
                # This is normal, when comparing IPv4 against IPv6.
                pass

        return False
