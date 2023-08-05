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
    A installed packages auditing plugin that should work with CentOS

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
"""
import abc
from subprocess import Popen, PIPE
import shlex
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class PackageManagerBase(object):
    """
    Base class for all the different linux package managers
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def list_packages(self):
        """
        @return: A dictionary of package name keys and package version values
        @rtype: C{dict(str: str)}
        """
        pass

class PackageManagerDpkg(PackageManagerBase):
    """
    Gets listing of packages and versions using dpkg
    """
    def list_packages(self):
        software = {}

        pkg_list_cmd = '/usr/bin/dpkg -l'
        pkg_list_out = Popen(shlex.split(pkg_list_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('pkg_list command results [%s]: %s', pkg_list_cmd, pkg_list_out)

        for line in pkg_list_out:
            cols = line.strip().split()
            if cols[0] == 'ii' and len(cols) >= 3:
                software[cols[1]] = cols[2]

        return software

class PackageManagerRpm(PackageManagerBase):
    """
    Gets listing of packages and versions using rpm
    """
    def list_packages(self):
        software = {}

        pkg_list_cmd = '/bin/rpm -qa --queryformat="%{NAME} %{VERSION}\\n"'
        pkg_list_out = Popen(shlex.split(pkg_list_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('pkg_list command results [%s]: %s', pkg_list_cmd, pkg_list_out)

        for line in pkg_list_out:
            cols = line.strip().split()
            if len(cols) >= 2:
                software[cols[0]] = cols[1]

        return software

