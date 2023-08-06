# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import sys
from setuptools import setup
from setuptools import find_packages

version = '1.0'

install_requires = [ 'setuptools', ]
if sys.version_info < (2, 7):
    install_requires.append('unittest2')


setup(
    name='unittest_jshint',
    version=version,
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/garbas/unittest_jshint',
    description="python unittest integration for jshint",
    long_description=open('README.rst').read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'jshint=unittest_jshint:run_jslint',
            ],
        },
    )
