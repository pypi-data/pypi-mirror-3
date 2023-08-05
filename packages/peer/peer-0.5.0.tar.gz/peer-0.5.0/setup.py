# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

import fnmatch
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def recursive_include(directory, patterns):
    result = []
    for root, dirs, files in os.walk(directory):
        child_root = root.replace(directory, '').lstrip('/')
        for pattern in patterns:
            result.extend([os.path.join(child_root, name)
                           for name in fnmatch.filter(files, pattern)])
    return result

# be careful with the syntax of this line since it is parsed from
# the docs/conf.py file
VERSION = '0.5.0'

setup(
    name='peer',
    version=VERSION,
    url='https://github.com/Yaco-Sistemas/peer',
    license='BSD',
    description=('Public Endpoint Entities Registry'),
    long_description=(read('README') + '\n\n' + read('CHANGES')),
    author='Terena',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    packages=find_packages('.'),
    package_dir={'peer': 'peer'},
    package_data={
        'peer': recursive_include('peer', ['*.html', '*.css', '*.js',
                                           '*.png', '*.ico', '*.wsgi'])
        },
    zip_safe=False,
    install_requires=[
        'Django>=1.3',
        'South',
        'psycopg2',
        'django-registration==0.7',
        'django-recaptcha==0.0.1',
        'fudge',
        'django-vff==0.1b1',
        'lxml',
        'pygments',
        ],
)
