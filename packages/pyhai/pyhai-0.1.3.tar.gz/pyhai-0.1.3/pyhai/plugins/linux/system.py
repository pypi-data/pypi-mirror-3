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
    A basic system auditing plugin that should work with most Redhat-like distros

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
from pyhai.plugins import AuditorPlugin
import platform
try:
    import platform.linux_distribution as distribution
except: import platform.dist as distribution
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class SystemPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        return {
            'uname': platform.uname(),
            'architecture': platform.architecture()[0],
            'platform': platform.platform(),
            'release': platform.release(),
            'system': platform.system(),
            'version': platform.version(),
            'distribution': distribution(),
            }
