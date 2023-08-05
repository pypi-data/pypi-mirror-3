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
    A memory auditing plugin that should work on most Redhat-like distros

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class MemoryPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        memory_info = {}

        with open('/proc/meminfo') as fp:
            for line in fp.read().splitlines():
                name_value = map(str.strip, str.split(line, ':', 1))
                if len(name_value) != 2:
                    continue
                name, value = name_value

                if name == 'MemFree':
                    memory_info['available_bytes'] = long(value.split()[0])
                elif name == 'MemTotal':
                    memory_info['total_bytes'] = long(value.split()[0])
                if name == 'SwapFree':
                    memory_info['available_swap_bytes'] = long(value.split()[0])
                elif name == 'SwapTotal':
                    memory_info['total_swap_bytes'] = long(value.split()[0])
                if name == 'VmallocFree':
                    memory_info['available_virtual_bytes'] = long(value.split()[0])
                if name == 'VmallocTotal':
                    memory_info['total_virtual_bytes'] = long(value.split()[0])

        return memory_info

