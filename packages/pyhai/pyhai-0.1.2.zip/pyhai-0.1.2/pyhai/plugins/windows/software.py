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
    Attempts to list the installed software on a windows host

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
import logging

win32com = None

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

try:
    from win32com.client import GetObject
except:
    _logger.exception('%s failed to import required Windows specific modules: %s', __name__, ', '.join('win32com.client.GetObject',))
    raise

class SoftwarePlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        product_info = {}

        wmi = GetObject(r'winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2')
        products = wmi.ExecQuery('SELECT Name, Version FROM Win32_Product')

        for product in products:
            _logger.debug('Found %s: %s', product.Name, product.Version)
            product_info[(str(product.Name))] = str(product.Version)

        return product_info

