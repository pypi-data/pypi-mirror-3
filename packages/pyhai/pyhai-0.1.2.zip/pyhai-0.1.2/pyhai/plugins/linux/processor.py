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
    A processor auditing plugin that should work with most Redhat-like distros

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

class ProcessorPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        processor_info = {}

        cpu_index = None
        with open('/proc/cpuinfo') as fp:
            for line in fp.read().splitlines():
                name_value = map(str.strip, str.split(line, ':', 1))
                if len(name_value) != 2:
                    continue
                name, value = name_value
                if name == 'processor':
                    cpu_index = value
                    if cpu_index not in processor_info:
                        processor_info[cpu_index] = {}

                if cpu_index is None:
                    continue

                if name == 'cpu MHz':
                    processor_info[cpu_index]['mhz'] = value
                elif name == 'model name':
                    processor_info[cpu_index]['identifier'] = value
                    processor_info[cpu_index]['name_string'] = value
                elif name == 'vendor_id':
                    processor_info[cpu_index]['vendor_identifier'] = value

        return processor_info

