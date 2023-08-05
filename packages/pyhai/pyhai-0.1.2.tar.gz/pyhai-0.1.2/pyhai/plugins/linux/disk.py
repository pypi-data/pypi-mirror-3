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
    A disk auditing plugin that should work with most Redhat-like distros

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
from pyhai import AuditorPlugin
from subprocess import Popen, PIPE
import shlex
import logging

# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class DiskPlugin(AuditorPlugin):
    def run(self, *args, **kwargs):

        drive_info = {}

        df_cmd = 'df -PT'
        df_out = Popen(shlex.split(df_cmd), stdout=PIPE).stdout.read().splitlines()
        _logger.debug('Output from df command [%s]: %s', df_cmd, df_out)
        df_headers = df_out[0].split()
        df_table = df_out[1:]
        try:
            block_size = int(df_headers[2].split('-')[0])
        except:
            _logger.exception('Could not coax block size into an integer: %s', headers[1])
            return drive_info

        for row in df_table:
            columns = row.split()
            drive = columns[6]
            if drive not in drive_info:
                drive_info[drive] = {}

            drive_info[drive]['total_bytes'] = long(long(columns[2]) / block_size)
            drive_info[drive]['available_bytes'] = long(long(columns[4]) / block_size)
            drive_info[drive]['label'] = columns[0]
            drive_info[drive]['filesystem'] = columns[1]


        return drive_info
