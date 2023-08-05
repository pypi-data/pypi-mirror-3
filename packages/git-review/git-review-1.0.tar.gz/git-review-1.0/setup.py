#!/usr/bin/python
# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

# Please also change this in git-review when changing it.
version = '1.0'

cmdclass = {}

# If Sphinx is installed on the box running setup.py,
# enable setup.py to build the documentation, otherwise,
# just ignore it
try:
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            for builder in ['html', 'man']:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    cmdclass['build_sphinx'] = local_BuildDoc

except:
    pass

setup(
    name='git-review',
    version=version,
    description="Tool to submit code to Gerrit",
    license='Apache License (2.0)',
    classifiers=["Programming Language :: Python"],
    keywords='git gerrit review',
    author='OpenStack, LLC.',
    author_email='openstack@lists.launchpad.net',
    url='http://www.openstack.org',
    include_package_data=True,
    #packages=find_packages(exclude=['test', 'bin']),
    scripts=['git-review'],
    zip_safe=False,
    cmdclass=cmdclass,
    install_requires=['setuptools'],
    test_suite='nose.collector',
    )
