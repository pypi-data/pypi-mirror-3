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

from os import makedirs
from os.path import exists
from setuptools import setup

from expel.lib.support import settings
paths = settings.paths()

setup(name='expel.apps.echo',
    version='0.1',
    description='xPL Echo - Echos all messages received from the xPL hub.',
    long_description=open('README.txt').read(),
    author='Simon Kennedy',
    author_email='code@sffjunkie.co.uk',
    url="http://www.sffjunkie.co.uk/python-expel.html#echo",
    license='Apache-2.0',
    scripts=['xplecho.py'],
    install_requires=['expel.lib>=0.2', 'expel.message'],
    data_files = [
        (paths['ConfigDirectory'], ['sffj-echo.ini']),
    ],
)
