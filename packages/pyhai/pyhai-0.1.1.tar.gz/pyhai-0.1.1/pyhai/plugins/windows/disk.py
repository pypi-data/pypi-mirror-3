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
    A disk auditing plugin that should work on most Windows systems

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

class DiskPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):

        drive_info = {}
        drives = win32api.GetLogicalDriveStrings().split('\0')

        for drive in drives:
            if drive not in drive_info:
                drive_info[drive] = {}

            try:
                volume_info = win32api.GetVolumeInformation(drive)
            except:
                continue

            drive_info[drive]['label'] = volume_info[0]
            drive_info[drive]['serial_number'] = volume_info[1]
            drive_info[drive]['file_system'] = volume_info[4]

            space_info = win32api.GetDiskFreeSpaceEx(drive)
            drive_info[drive]['available_bytes'] = space_info[0]
            drive_info[drive]['total_bytes'] = space_info[1]

        return drive_info
