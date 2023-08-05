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
    A cross-platform hostname plugin

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
from pyhai.plugins import AuditorPlugin
import socket
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class HostnamePlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        fqdn = socket.getfqdn()
        hostname = socket.gethostname()
        fqdn_resolved_ip = None
        hostname_resolved_ip = None
        try:
            fqdn_resolved_ip = socket.gethostbyname(fqdn)
        except socket.gaierror:
            _logger.exception('Failed to resolve FQDN: %s', fqdn)

        try:
            hostname_resolved_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            _logger.exception('Failed to resolve hostname: %s', hostname)

        return {
            'fqdn': fqdn,
            'fqdn_resolved_ip': fqdn_resolved_ip,
            'hostname': hostname,
            'hostname_resolved_ip': hostname_resolved_ip,
            }
