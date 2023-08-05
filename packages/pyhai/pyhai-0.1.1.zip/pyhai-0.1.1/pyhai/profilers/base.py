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
    pyHai profiler base class

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""

import abc

class ProfilerBase(object):
    """
    An ABC class to enforce a common profiler interface
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def profile(self):
        """
        Profile's the local system
        
        @return: A dictionary of properties discovered about the local system
        @rtype: C{dict}
        """
        pass

    @abc.abstractmethod
    def system(self):
        """
        Returns the system property for use in resolving plugins
        
        @return: The name of the current type of system
        @rtype: C{str}
        """
        pass

    @abc.abstractmethod
    def system_class(self):
        """
        Returns the system class property for use in resolving plugins
        
        @return: The name of the current type of system class
        @rtype: C{str}
        """
        pass
