import ipaddress


class IpRangeList:
    def __init__(self, whitelist):
        self.whitelist = whitelist

    def matches(self, ip):
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
