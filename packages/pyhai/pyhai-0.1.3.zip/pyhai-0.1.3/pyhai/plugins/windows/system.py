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
    A basic system information plugin that should work with most Windows systems

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
from pyhai.plugins import AuditorPlugin
import platform
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

class SystemPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):

        return {
            'computer_name': win32api.GetComputerName(),
            'domain': win32api.GetDomainName(),
            'uname': platform.uname(),
            'architecture': platform.architecture()[0],
            'platform': platform.platform(),
            'release': platform.release(),
            'system': platform.system(),
            'version': platform.version(),
            }
