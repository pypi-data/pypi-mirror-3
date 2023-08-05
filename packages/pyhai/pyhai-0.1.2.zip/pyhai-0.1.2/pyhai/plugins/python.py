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
    A cross-platform Python auditor plugin

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
import platform
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class PythonPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):
        return {
            'python_build': platform.python_build(),
            'python_compiler': platform.python_compiler(),
            'python_branch': platform.python_branch(),
            'python_implementation': platform.python_implementation(),
            'python_revision': platform.python_revision(),
            'python_version': platform.python_version(),
            'python_version_tuple': platform.python_version_tuple(),
            }
