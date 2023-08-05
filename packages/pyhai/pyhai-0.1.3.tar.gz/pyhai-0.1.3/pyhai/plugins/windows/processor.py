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
    A processor auditor that should work on most Windows hosts

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
from pyhai.plugins import AuditorPlugin
import sys
import logging

win32api = None
win32con = None

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

try:
    import win32api
    import win32con
except:
    _logger.exception('%s failed to import required Windows specific modules: %s', __name__, ', '.join('win32api', 'win32con'))
    raise

class ProcessorPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        processor_info = {}
        processor_description_key_path = 'HARDWARE\DESCRIPTION\System\CentralProcessor'
        system_env_vars_key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, processor_description_key_path)
        value_index = 0
        try:
            while True:
                cpu_index = win32api.RegEnumKey(system_env_vars_key, value_index)
                cpu_reg = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, processor_description_key_path + '\\' + cpu_index)
                processor_info[cpu_index] = {
                    'mhz': win32api.RegQueryValueEx(cpu_reg, '~MHz')[0],
                    'identifier': win32api.RegQueryValueEx(cpu_reg, 'Identifier')[0],
                    'name_string': win32api.RegQueryValueEx(cpu_reg, 'ProcessorNameString')[0],
                    'vendor_identifier': win32api.RegQueryValueEx(cpu_reg, 'VendorIdentifier')[0],
                    }
                value_index += 1
        except:
            exc_id = sys.exc_info()[1][0]
            if exc_id != 259: # 259 == 'No more data is available.'
                raise

        processor_info['count'] = len(processor_info)

        return processor_info
