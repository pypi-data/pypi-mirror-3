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
    A default implementation of the profiler

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
import platform
import socket
import base

class DefaultProfiler(base.ProfilerBase):
    """
    The default profiler plugin
    """
    __profile = None

    def __init__(self):
        """
        Initialize profiler
        """
        system_class = str(platform.system().lower())
        system = self.__detect_system(system_class)
        self.__profile = {
            'system_class': system_class,
            'system': system,
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            }

    def profile(self):
        """
        Returns the system's profile
        
        @return: A dictionary consisting of the system and architecture
        @rtype: C{dict}
        """
        return self.__profile

    def system(self):
        """
        Returns the system property of the system's profile
        
        @return: The system property of the system's profile
        @rtype: C{str}
        """
        return self.__profile['system']

    def system_class(self):
        """
        Returns the system class property - windows, linux, java
        
        @return: The type of system
        @rtype: C{str}
        """
        return self.__profile['system_class']

    def __detect_system(self, system_class):
        """
        Detects the specific type of system. For windows, the windows type and version,
        for linux, the distribution and version
        
        @return: A string representing the specific type of system: windows7, windowsxp, ubuntu, centos, etc
        @rtype: C{str}
        """
        if system_class == 'linux':
            if hasattr(platform, 'linux_distribution'):
                distro = platform.linux_distribution()
            elif hasattr(platform, 'dist'):
                distro = platform.dist()
            else:
                distro = None
            if distro and type(distro) is tuple and len(distro) > 0:
                system = str(distro[0]).lower()
                system_parts = system.split()
                if system_parts[0] in ('centos'):
                    return system_parts[0]
                else:
                    return system
        elif system_class == 'windows':
            return str(platform.win32_ver()[0]).lower()
        else:
            return None
