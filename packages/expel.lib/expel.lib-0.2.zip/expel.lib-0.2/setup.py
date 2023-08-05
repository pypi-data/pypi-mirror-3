# Copyright 2009-2011, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from setuptools.command.install import install as install_

from expel.lib.support import settings

class install(install_):
    def run(self):
        p = settings.paths()
        p.create()
        
        x = settings.xpl()
        x.create()
        
        install_.run(self)


setup(name='expel.lib',
    version='0.2',
    description='Generate and respond to xPL messages.',
    long_description=open('README.txt').read(),
    author='Simon Kennedy',
    author_email='code@sffjunkie.co.uk',
    url="http://www/sffjunkie.co.uk/python-expel.html",
    license='Apache-2.0',
    packages=find_packages(exclude=['expel.test']),
    namespace_packages=['expel'],
    install_requires=['expel.message', 'configobj', 'twisted'],
    cmdclass={'install': install},
)

