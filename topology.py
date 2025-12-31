from mininet.topo import Topo
from mininet.node import Node
from mininet.link import TCLink

# mn --custom topology.py --topo courseworkTopo --switch=lxbr --link=tc --controller=none


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        if 'routes' in params:
            for (ip, gateway) in params['routes']:
                self.cmd('ip route add {} via {}'.format(ip, gateway))
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class courseworkTopo(Topo):

    def build(self):
        # add a host to the network with IP 10.1.1.1
        host1 = self.addHost('host1', ip="192.168.0.2/24",
                             defaultRoute='via 192.168.0.1')

        host2 = self.addHost('host2', ip="192.168.0.3/24",
                             defaultRoute='via 192.168.0.1')

        host3 = self.addHost('host3', ip="192.168.2.2/24",
                             defaultRoute="via 192.168.2.1")

        host4 = self.addHost('host4', ip="192.168.2.3/24",
                             defaultRoute="via 192.168.2.1")

        host5 = self.addHost('host5', ip="192.168.3.2/24",
                             defaultRoute="via 192.168.3.1")

        # Add router1: 192.168.3.0/24 via 10.10.1.2, 192.168.2.0/24 via 10.10.0.1
        router1 = self.addNode('router1', cls=LinuxRouter, ip=None,
                               routes=[("192.168.3.0/24", "10.10.1.2"), ("192.168.2.0/24", "10.10.0.1")])

        # Add router2: 192.168.0.0/24 via 10.10.0.2, 10.10.1.0/24 via 10.10.0.2, 192.168.3.0/24 via 10.10.0.2
        router2 = self.addNode('router2', cls=LinuxRouter, ip=None,
                               routes=[("192.168.0.0/24", "10.10.0.2"), ("10.10.1.0/24", "10.10.0.2"),
                                       ("192.168.3.0/24", "10.10.0.2")])

        # Add router3: 192.168.0.0/24 via 10.10.1.1, 10.10.0.0/24 via 10.10.1.1, 192.168.2.0/24 via 10.10.1.1
        router3 = self.addNode('router3', cls=LinuxRouter, ip=None,
                               routes=[("192.168.0.0/24", "10.10.1.1"), ("10.10.0.0/24", "10.10.1.1"),
                                       ("192.168.2.0/24", "10.10.1.1")])

        # add a switch to the network
        switch1 = self.addSwitch('switch1')

        switch2 = self.addSwitch('switch2')

        # Add links
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)

        self.addLink(switch1, router1, intfName2='eth1',
                     params2={'ip': '192.168.0.1/24'})

        self.addLink(router1, router2, delay="10ms", loss=1, intfName1='eth2', params1={
                     'ip': '10.10.0.2/24'}, intfName2='eth2', params2={'ip': '10.10.0.1/24'})

        self.addLink(router1, router3, bw=100, delay="100ms", intfName1='eth3', params1={
                     'ip': '10.10.1.1/24'}, intfName2='eth2', params2={'ip': '10.10.1.2/24'})

        self.addLink(switch2, router2, intfName2='eth1', params2={
                     'ip': '192.168.2.1/24'})

        self.addLink(router3, host5, intfName1='eth0', params1={
                     'ip': '192.168.3.1/24'})


# mn --custom topology.py --topo courseworkTopo --switch=lxbr --link=tc --controller=none
# the topologies accessible to the mn tool's `--topo` flag
# note: if using the Dockerfile, this must be the same as in the Dockerfile
topos = {'courseworkTopo': (lambda: courseworkTopo())}
