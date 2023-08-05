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
    pyHai auditor plugin base class

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
import abc

import logging
# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class AuditorPlugin(object):
    """
    An ABC class to enforce a common plugin interface
    """
    __metaclass__ = abc.ABCMeta

    __profile = None
    __results = None
    _running_audit = None


    def __init__(self, profile, running_audit_results, *args, **kwargs):
        """
        You probably shouldn't overwrite this method unless you know what you're doing and
        even then you should be careful and call Plugin.__init__.py at some point.
        I{Swim at your own risk}
        
        @param profile: A dictionary containing this host's profile
        @type profile: C{dict}
        @param running_audit_results: A dictionary of the results of all the plugins that have run up to "now"
        @type running_audit_results: C{dict}
        @return: A dictionary of results from the plugin's run
        @rtype: C{dict}
        """
        self.__profile = profile
        self._running_audit = running_audit_results
        try:
            before_results = self.before(*args, **kwargs)
            self.__set_results(self.run(*args, before_results=before_results, **kwargs))
            self.__set_results(self.after(*args, **kwargs))
        except Exception as exc:
            self.fail(exc)

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        """
        Will be called after the before hook.
        This is the only "required" method for plugins
        """
        pass

    def before(self, *args, **kwargs):
        """
        Overwrite in subclass as necessary
        Will be called first during init
        """
        _logger.debug('Plugin hook "before" is not overwritten')
        return None

    def after(self, *args, **kwargs):
        """
        Overwrite in subclass as necessary
        Will be called first during init
        """
        _logger.debug('Plugin hook "after" is not overwritten')
        return self._get_results()

    def fail(self, exc, msg=None, *args):
        """
        Overwrite in subclass as necessary
        Will be called for any exceptions raised for before, run, or after methods
        """
        _logger.debug('Current state of results in %s: %s',)
        _logger.exception(msg, *args)

    def get_profile(self, key=None):
        """
        Gets the entire profile dictionary, a list of items or a single key from the profile dictionary
        
        @param key: Providing a string returns a single value from the profile dictionary,
            providing an array, returns a slice of the profile dictionary, omitting this param
            returns the entire profile dictionary
        @type key: C{list | str}
        @return: Mixed... part or all of the profile dictionary
        @rtype: C{dict | str}
        """
        if key is not None:
            if type(key) is list:
                return dict([(k, self.__profile[k]) for k in key if k in self.__profile])
            elif type(key) is str and key in self.__profile:
                return self.__profile[key]
            else:
                return None
        else:
            return self.__profile

    def __set_results(self, results):
        """
        Ensures that only dict types are stored in the __results instance var
        
        @param results: The results from the plugin_hooks or the run
            B{**MUST} be a dict or will raise an exception 
        @type results: C{dict}
        """
        result_type = type(results)
        if result_type is dict or result_type is tuple or result_type is list:
            self.__results = results

    def _get_results(self):
        """
        Returns results
        
        @return: Results of the run
        @rtype: C{dict}
        """
        return self.__results
