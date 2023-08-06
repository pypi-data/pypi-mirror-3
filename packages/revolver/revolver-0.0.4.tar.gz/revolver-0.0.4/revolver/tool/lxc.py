# -*- coding: utf-8 -*-

from revolver import contextmanager as ctx
from revolver import file
from revolver import package
from revolver import service
from revolver.core import run, sudo

_DHCP_CONFIG = """
domain-needed
bogus-priv
interface = br0
listen-address = 127.0.0.1
listen-address = %(bridge_ip)s
expand-hosts
domain = lxc
dhcp-range = %(bridge_dhcp_start)s,%(bridge_dhcp_end)s,%(bridge_dhcp_ttl)s
"""

_DNS_CONFIG = """
prepend domain-name-servers 127.0.0.1;
prepend domain-search "containers.";
"""

def install(nat_device="eth0", bridge_device="br0", bridge_ip="192.168.3.1",
            bridge_dhcp_start="192.168.3.50", bridge_dhcp_end="192.168.3.200",
            bridge_dhcp_ttl="1h"):
    package.install(['lxc', 'debootstrap', 'bridge-utils', 'dnsmasq'])

    # TODO: Store everything reboot-proof!
    with ctx.sudo():
        # Create the new adapter
        status = run('brctl show %(bridge_device)s | tail -n1' % locals())
        if status.find("No such device") != -1:
            run('brctl addbr %(bridge_device)s' % locals())
            run('brctl setfd %(bridge_device)s 0' % locals())

        # Ensure the bridge is configured and up
        run('ifconfig br0 %(bridge_ip)s up' % locals())

        # Let them access eth0 (network / internet)
        run('iptables -t nat -A POSTROUTING -o %(nat_device)s -j MASQUERADE' % locals())
        run('sysctl -w net.ipv4.ip_forward=1')

        # Setup DHCP / DNS
        file.write('/etc/dnsmasq.d/lxc', _DHCP_CONFIG % locals())
        file.append(_DNS_CONFIG % locals(), '/etc/dhcp/dhclient.conf')

        # And finally restart some services
        service.restart('dnsmasq')

# TODO: Implement ensure()
