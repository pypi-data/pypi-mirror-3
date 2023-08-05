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
    A network auditing plugin that should work on most Windows systems

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
from pyhai.plugins import AuditorPlugin
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

try:
    from win32com.client import GetObject
except:
    _logger.exception('%s failed to import required Windows specific modules: %s', __name__, ', '.join('win32com.client.GetObject',))
    raise

class NetworkPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        network_info = {}

        wmi = GetObject(r'winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2')
        network_adaptor_configurations = wmi.ExecQuery('SELECT * FROM Win32_NetworkAdapterConfiguration WHERE IPEnabled = TRUE')
        network_adaptors = wmi.ExecQuery('SELECT * FROM Win32_NetworkAdapter')

        for nic_config in network_adaptor_configurations:
            if not nic_config.IPEnabled:
                continue

            config_index = str(nic_config.Index)
            if config_index not in network_info:
                network_info[config_index] = {}

            network_info[config_index]['dns_servers'] = [str(host) for host in self._get_or_list(nic_config.DNSServerSearchOrder)]
            network_info[config_index]['dhcp_enabled'] = nic_config.DHCPEnabled
            network_info[config_index]['dhcp_server'] = nic_config.DHCPServer
            network_info[config_index]['ip_address'] = [str(ip) for ip in self._get_or_list(nic_config.IPAddress)]
            network_info[config_index]['subnet_mask'] = [str(sm) for sm in self._get_or_list(nic_config.IPSubnet)]
            network_info[config_index]['default_gateway'] = [str(dg) for dg in self._get_or_list(nic_config.DefaultIPGateway)]
            network_info[config_index]['mac_address'] = nic_config.MACAddress
            network_info[config_index]['wins_servers'] = [str(nic_config.WINSPrimaryServer), str(nic_config.WINSSecondaryServer)]

        for nic in network_adaptors:
            nic_index = str(nic.Index)
            if nic_index not in network_info:
                continue

            network_info[nic_index]['name'] = nic.Name
            network_info[nic_index]['label'] = nic.NetConnectionID
            network_info[nic_index]['manufacturer'] = nic.Manufacturer
            network_info[nic_index]['device_id'] = nic.PNPDeviceID
            network_info[nic_index]['guid'] = nic.GUID
            network_info[nic_index]['speed'] = nic.Speed

        return network_info

    def _get_or_list(self, obj):
        try:
            if obj:
                return obj
            else:
                return list()
        except:
            return list()
