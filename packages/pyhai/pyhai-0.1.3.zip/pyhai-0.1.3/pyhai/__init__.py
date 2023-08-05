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
    pyHai base classes

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.3
@date: Jan 19, 2012
"""
import abc
import os
import sys
import datetime
import time
import utils
import profilers.base
import profilers.default

import logging
# set some default logging behavior
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

# current version
__VERSION__ = (0, 1, 3)
VERSION = '.'.join(map(str, __VERSION__))

# set some default variables
PACKAGE_PLUGIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
DEFAULT_CUSTOM_PLUGIN_PATH = os.path.join(os.path.dirname(os.path.abspath('.')), 'plugins')
PLUGIN_LOADER_EXCLUSIONS = ('.', '..', '__init__.py', '__init__.pyc', '__init__.pyo')
DEFAULT_PROFILER_CLASS = profilers.default.DefaultProfiler


class Auditor(object):
    """
    Auditor class
    
    @ivar custom_plugin_path: The path to any custom plugins
    @type custom_plugin_path: C{str}
    @ivar profile: A dictionary of properties for this host
    @type profile: C{dict}
    @ivar architecture: The name of the architecture as is normally returned by platform.architecture()[0]
    @type architecture: C{str}
    @ivar plugins: A list of successfully loaded plugins
    @type plugins: C{list}
    """
    plugin_paths = [PACKAGE_PLUGIN_PATH]
    profile = None
    plugins = {}

    def __init__(self, plugin_paths=None, **kwargs):
        """
        Initialize System object
        
        @param plugin_paths: A path (or list of paths) to a custom set of plugins
        @type plugin_paths: C{str | list}
        @keyword profiler_class: The name of a class that extends L{ProfilerBase} or the name of the module where the
            L{ProfilerBase} class can be found. If supplying a module, must supply the profiler_class keyword arg
        @type profiler_class: C{class | str}
        @keyword enable_default_plugins: A flag to use (or suppress) the builtin plugins
        @type enable_default_plugins: C{bool}
        @keyword profiler_package: The name of the package that contains a class that extends L{ProfilerBase}
        @type profiler_package: C{str} 
        """
        profiler_class = kwargs.get('profiler_class', DEFAULT_PROFILER_CLASS)
        profiler_package = kwargs.get('profiler_package', None)
        enable_default_plugins = kwargs.get('enable_default_plugins', True)


        if type(profiler_class) is str:
            profiler_package = kwargs.get('profiler_package', '')
            if profiler_package:
                profiler_class = self.__load_module(profiler_package, profiler_class)
            else:
                profiler_class = self.__load_module(profiler_class)

        if issubclass(profiler_class, profilers.base.ProfilerBase):
            profiler = profiler_class()
            if hasattr(profiler, 'profile'):
                self.profile = profiler.profile()
                if type(self.profile) is dict and 'pyhai_version' not in self.profile:
                    self.profile['pyhai_version'] = VERSION
                self.system_class = profiler.system_class()
                self.system = profiler.system()
                _logger.debug('Successfully loaded the profiler: %s', profiler.__class__.__name__)
            else:
                raise Exception('Failed to load a valid profiler: %s' % profiler.__class__.__name__)
        else:
            raise Exception('Arguments supplied for profiler are not valid')

        if plugin_paths:
            if type(plugin_paths) is str:
                plugin_paths = [plugin_paths]

            if enable_default_plugins:
                for path in plugin_paths:
                    if path not in self.plugin_paths:
                        self.plugin_paths.append(path)
            else:
                self.plugin_paths = plugin_paths
        elif not plugin_paths and not enable_default_plugins:
            # TODO: Is there a better way to do this? Would like to stop execution and allow for exception information to
            #    be sent to the logger.
            try:
                raise ValueError('Incompatible init params... plugin_paths is empty and enable_default_plugins=False')
            except:
                _logger.exception('Must provide a list for plugin_paths or set enable_default_plugins=True. Nothing to do.')
                raise

        for path in self.plugin_paths:
            sys.path.insert(0, path)
        _logger.debug('Setting plugin_paths to: ["%s"]', '", "'.join(self.plugin_paths))
        self.__load_plugins(self.system_class, self.system)


    def __load_profiler(self, profiler, package=''):
        """
        Loads a profiler plugin
        
        @param profiler: The name of a class that extends L{ProfilerBase}
        @type profiler: C{str}
        @param package: The name of the package where the profiler exists
        @type package: C{str}
        """
        return self.__load_module(profiler, package)


    def __load_plugins(self, system_class, system, plugin_module=None):
        """
        Imports plugin modules and stores the list of successfully loaded plugins
        
        @param plugin_module: A specific plugin_module to load
        @type plugin_module: C{str}
        """
        _logger.info('Loading plugins...')
        if plugin_module:
            raise NotImplementedError('Planned for future release')
        else:
            plugin_map = self.__resolve_plugin_paths(system_class, system)
            for plugin, (path, namespace) in plugin_map.items():
                _logger.debug('Loading plugin: %s, path: %s, package: %s', plugin, path, namespace)
                if path not in sys.path:
                    sys.path.insert(0, path)
                try:
                    plugin_class = '%s%s' % (utils._underscore_to_camel_case(plugin), 'Plugin')
                    self.plugins[plugin] = self.__load_module(namespace, plugin_class)
                    _logger.debug('Loaded plugin: %s [%s::%s]', plugin, namespace, plugin_class)
                except:
                    _logger.exception('Failed to load plugin: %s [%s::%s]', plugin, namespace, plugin_class)


    def __load_module(self, module, cls=''):
        """
        Loads a module and class dynamically return a reference to the class
        
        @param module: The name of module to load
        @type module: C{str}
        @param cls: The name of a class to load
        @type cls: C{str}
        @return: A reference to the loaded class
        @rtype: C{class}
        """
        try:
            module_instance = __import__(module, globals(), locals(), [cls])
            if cls and hasattr(module_instance, cls):
                _logger.debug('Successfully loaded module: %s, class: %s', module, cls)
                return getattr(module_instance, cls)
        except:
            _logger.exception('Failed to import module: %s, class: %s', module, cls)
            raise


    def __resolve_plugin_paths(self, system_class, system, **kwargs):
        """
        Checks plugin paths for validity and returns only those that are valid

        @param system: The type of system
        @type system: C{str}
        @keyword plugin_paths: A path (or list of paths) to a custom set of plugins
        @type plugin_paths: C{str}|C{list}
        @return: A list of valid plugin paths
        @rtype: C{list}
        """
        plugins = {}
        plugin_paths = kwargs.get('plugin_paths', self.plugin_paths)
        for plugin_path in plugin_paths:
            _logger.debug('Searching plugin path: %s', plugin_path)
            system_class_path = os.path.join(plugin_path, system_class)
            system_path = os.path.join(system_class_path, system)

            valid_plugins = self.__validate_plugins(plugin_path)
            valid_plugins = self.__validate_plugins(system_class_path, system_class, valid_plugins)
            valid_plugins = self.__validate_plugins(system_path, '%s.%s' % (system_class, system), valid_plugins)

            if valid_plugins is not None and len(valid_plugins) > 0:
                _logger.debug('Merging plugins dictionaries')
                plugins = dict(plugins.items() + valid_plugins.items())

        return plugins


    def __validate_plugins(self, path, base=None, plugins=None):
        """
        Performs an initial sanity check on all the plugins found in a path
        
        @param path: The path to look for plugins
        @type path: C{str}
        @param base: The base of the package name if path is a subfolder of a python package
            - I{To assist with the import, i.e. from package.module import plugin}
        @type base: C{str}
        """
        if plugins is None:
            _logger.debug('Creating plugins dict')
            plugins = {}

        if os.path.exists(path) and os.path.isdir(path):
            for plugin_entry in os.listdir(path):
                _logger.debug('Validating file as plugin: %s', plugin_entry)
                if plugin_entry in PLUGIN_LOADER_EXCLUSIONS or os.path.isdir(plugin_entry) or not plugin_entry.endswith('.py') or plugin_entry.startswith('_'):
                    continue

                plugin = plugin_entry[:-3]
                package = plugin

                if base is not None:
                    package = '%s.%s' % (base, plugin)
                    _logger.debug('package: %s', package)

                _logger.debug('File appears to be a valid plugin: %s, package: %s [%s]', plugin, package, os.path.join(path, plugin_entry))

                plugins[plugin] = (path, package)

        return plugins


    def audit(self, convert_date_to_iso=True):
        """
        Profiles the system using the default plugins and all custom plugins, returning a dictionary of the results
        
        @param convert_date_to_iso: Converts the 'audit_completed' date to iso format before returning
        @type convert_date_to_iso: C{bool}
        @return: A dictionary representing the current state of the system
        @rtype: C{dict}
        """
        start = time.time()
        if len(self.plugins) <= 0:
            # TODO: Same deal as TODO in class __init__...
            try:
                raise ValueError('No plugins found')
            except:
                _logger.exception('List of plugins is empty. Nothing to do.')
                raise

        results = {'profile': self.profile}
        for plugin_name, plugin_class in self.plugins.items():
            _logger.debug('Running plugin: %s [%s]', plugin_name, plugin_class.__name__)
            plugin = plugin_class(self.profile, results)
            results[plugin_name] = plugin._get_results()
        end = time.time()
        now = datetime.datetime.now()
        if convert_date_to_iso:
            results['profile']['audit_completed'] = now.isoformat()
        else:
            results['profile']['audit_completed'] = now
        results['profile']['audit_took_sec'] = end - start
        return results



def audit(plugin_paths=DEFAULT_CUSTOM_PLUGIN_PATH, **kwargs):
    """
    Instatiates a System object and executes it's profile method
    
    @param plugin_paths: A path (or list of paths) to a custom set of plugins
    @type plugin_paths: C{str}|C{list}
    @keyword debug: Set the logging level to DEBUG
    @type debug: C{bool}
    """
    debug = kwargs.pop('debug', False)

    if debug:
        _logger.setLevel(logging.DEBUG)

    auditor = Auditor(plugin_paths, **kwargs)
    return auditor.audit()
