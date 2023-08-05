"""
Copyright 2011 Mark LaPerriere

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
_version = '0.1.2'
from distutils.core import setup

setup(
    name='pyhai',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    version=_version,
    packages=[
        'pyhai',
        'pyhai.plugins',
        'pyhai.plugins.linux',
        'pyhai.plugins.linux.ubuntu',
        'pyhai.plugins.linux.centos',
        'pyhai.plugins.windows',
        'pyhai.profilers',
        ],
    description='A system profiler/auditor written in Python that supports custom plugins.',
    long_description='A system profiler/auditor written in Python that supports custom plugins and a custom profiler. Custom plugins can superscede builtin plugins to allow for a great deal of flexibility. Plugins follow naming conventions for ease of use.',
    url='https://bitbucket.org/marklap/pyhai',
    download_url='https://bitbucket.org/marklap/pyhai/src/tip/src/dist/pyhai-%s.tar.gz' % _version,
    author='pyhai@mindmind.com',
    author_email='pyhai@mindmind.com',
    maintainer='pyhai@mindmind.com',
    maintainer_email='pyhai@mindmind.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        ],
)
