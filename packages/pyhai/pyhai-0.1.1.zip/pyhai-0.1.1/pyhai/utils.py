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
    pyHai utility functions

@author: Mark LaPerriere
@contact: pyhai@mindmind.com
@organization: Mind Squared Design / www.mindmind.com
@version: 0.1.0
@date: Sep 11, 2011
"""
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

def _camel_case_to_underscore(name):
    """
    Take a camel cased name and returns a lower cased, underscore seperated name
    
    @param name: A name in CamelCase
    @type name: C{str}
    @return: An underscore seperated name
    @rtype: C{str}
    """
    if not name:
        raise ValueError('Can not create underscore seperated name from an empty string')

    if len(name) <= 1:
        return name.lower()

    result = StringIO()
    name_length = len(name)
    result.write(name[0].lower())
    for c in range(1, name_length):
        if name[c].isupper():
            result.write('_')
        result.write(name[c].lower())

    return result.getvalue()

def _underscore_to_camel_case(name):
    """
    Take a underscore seperated name and return a camel case name
    
    @param name: An underscore seperated name
    @type name: C{str}
    @return: A name in CamelCase
    @rtype: C{str}
    """
    if not name:
        raise ValueError('Can not CamelCase an empty string')
    if len(name) <= 1:
        return name.upper()
    return name.replace('_', ' ').title().replace(' ', '')
