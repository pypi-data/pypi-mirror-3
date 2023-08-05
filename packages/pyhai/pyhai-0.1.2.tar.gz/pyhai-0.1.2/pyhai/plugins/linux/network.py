"""
@copyright: 2011 Mark LaPerriere

@license:
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    U{http://www.apache.org/licenses/LICENSE-2.0}

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

@summary:
    A network auditing plugin that should work with most Redhat-like distros

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
from subprocess import Popen, PIPE
import os
import shlex
import platform
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class NetworkPlugin(AuditorPlugin):

    def run(self, *args, **kwargs):
        network_info = {}

        ifconfig_cmd = '/bin/env ifconfig -a'
        ifconfig_out = Popen(shlex.split(ifconfig_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('ifconfig command results [%s]: %s', ifconfig_cmd, ifconfig_out)

        line_no = 0
        found_break = False
        nic = None
        for line in ifconfig_out:

            stripped_row = line.strip()
            if stripped_row == '':
                found_break = True
                continue

            row = stripped_row.split()

            if line_no == 0 or found_break:
                if found_break: found_break = False

                nic = row[0]

                if nic == 'lo':
                    nic = None
                    continue

                if nic not in network_info:
                    network_info[nic] = {}

                network_info[nic]['name'] = nic
                network_info[nic]['label'] = nic
                network_info[nic]['device_id'] = nic
                network_info[nic]['mac_address'] = row[4]

            if nic is not None:
                if row[0] == 'inet' and row[1].startswith('addr:'):
                    network_info[nic]['ip_address'] = row[1].split(':', 1)[1]
                    network_info[nic]['subnet_mask'] = row[3].split(':', 1)[1]

            line_no += 1


        try:
            distribution = platform.linux_distribution()[0]
        except:
            _logger.exception('Could not determine distribution.')
            return network_info

        dns_servers = []
        redhat_servers = ('CentOS Linux', 'Red Hat Enterprise Linux Server')
        if distribution in redhat_servers:
            dns_servers = self._redhat_dns_servers()

        for nic in network_info.keys():

            if distribution in redhat_servers:
                dhcp_enabled, dhcp_server = self._redhat_dhcp(nic)
                network_info[nic]['dhcp_enabled'] = dhcp_enabled
                network_info[nic]['dhcp_server'] = dhcp_server

                network_info[nic]['default_gateway'] = self._redhat_default_gateway()
                network_info[nic]['dns_servers'] = dns_servers
                network_info[nic]['speed'] = self._redhat_speed(nic)
                network_info[nic]['name'] = self._redhat_nic_name(nic)

        return network_info

    def _redhat_dhcp(self, nic):
        dhcp_enabled = False
        dhcp_servers = []
        dhcp_lease_report = '/var/lib/dhclient/dhclient-%s.leases' % nic
        if os.path.exists(dhcp_lease_report):
            with open(dhcp_lease_report) as fp:
                for line in fp.read().splitlines():
                    row = line.strip().split()
                    if len(row) >= 3:
                        if row[1] == 'dhcp-server-identifier' and row[2] not in dhcp_servers:
                            dhcp_servers.append(row[2])

        if dhcp_servers >= 1:
            dhcp_enabled = True
        return (dhcp_enabled, dhcp_servers)

    def _redhat_default_gateway(self):
        route_cmd = 'route -n'
        route_out = Popen(shlex.split(route_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('route comand output [%s]: %s', route_cmd, route_out)

        for line in route_out:
            row = line.strip().split()
            if row[3] in ('UG', 'G'):
                return [row[1], ]

        return []


    def _redhat_dns_servers(self):
        dns_servers = []
        with open('/etc/resolv.conf') as fp:
            for line in fp.read().splitlines():
                row = line.strip().split()
                if row[0] == 'nameserver':
                    if row[1] not in dns_servers:
                        dns_servers.append(row[1])
        return dns_servers

    def _redhat_nic_name(self, nic):
        with open('/var/log/dmesg') as fp:
            for line in fp.read().splitlines():
                row = map(lambda s: s.strip(':'), line.strip().split())
                if len(row) <= 1:
                    continue
                if row[0] == nic or row[0] == nic:
                    return row[1]
                elif row[1] == nic or row[1] == nic:
                    return row[2]
        return None

    def _redhat_speed(self, nic):
        ethtool_cmd = 'ethtool %s' % nic
        ethtool_out = Popen(shlex.split(ethtool_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('ethtool command output [%s]: %s', ethtool_cmd, ethtool_out)

        for line in ethtool_out:
            row = map(lambda s: s.strip(':'), line.strip().split())
            if len(row) >= 2:
                if row[0] == 'Speed':
                    if row[1].endswith('Mb/s'):
                        # convert to b/s
                        return str(int(row[1].replace('Mb/s', '')) * 1000 * 1000)
                    else:
                        return row[1]
        return None

