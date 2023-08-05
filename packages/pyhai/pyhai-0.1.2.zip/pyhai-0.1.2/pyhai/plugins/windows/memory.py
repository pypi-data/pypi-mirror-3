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
    A memory auditing plugin that should work on most Windows systems

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
import logging

win32api = None

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

try:
    import win32api
except:
    _logger.exception('%s failed to import required Windows specific modules: %s', __name__, ', '.join('win32api'))
    raise

class MemoryPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        memory = win32api.GlobalMemoryStatus()
        return {
            'total_bytes': memory['TotalPhys'],
            'available_bytes': memory['AvailPhys'],
            'total_virtual_bytes': memory['TotalVirtual'],
            'available_virtual_bytes': memory['AvailVirtual'],
            'total_page_file_bytes': memory['TotalPageFile'],
            'available_page_file_bytes': memory['AvailPageFile'],
            }
