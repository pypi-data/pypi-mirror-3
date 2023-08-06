# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import tarfile
import urllib2
from urlparse import urlparse

from paver.easy import *
from paver.setuputils import find_packages, find_package_data
import paver.misctasks
import paver.virtual

from paver.setuputils import install_distutils_tasks
install_distutils_tasks()

VERSION = '0.6.0'

OLDHEADER = """
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

HEADER = """
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

options(
    version=Bunch(
        number=VERSION,
        name="Moksha",
    ),
    package_data=find_package_data(),
    packages=find_packages(exclude=['ez_setup']),
    build_top=path("build"),
    build_dir=lambda: options.build_top / "Moksha",
    license=Bunch(
        extensions = set([
            ("py", "#"), ("js", "//")
        ]),
        exclude=set([
            './ez_setup',
            './data',
            './tg2env',
            './docs',
            # Things we don't want to add our license tag to
            './pip.py',
            './pavement.py',
            './moksha/widgets/feedtree/static',
            './moksha/widgets/misc/ptd/game/',
            './moksha/widgets/misc/ptd/static',
            './moksha/widgets/container/static/js',
            './moksha/model/vertical',
            './moksha/api/widgets/layout/static',
            './moksha/api/widgets/chat/static',
            './moksha/api/menus/static',
        ])
    ),
    virtualenv=Bunch(
        packages_to_install=['pip'],
        paver_command_line="required"
    ),
    server=Bunch(
        address="",
        port=8080,
        try_build=False,
        dburl=None,
        async=False,
        config_file=path("development.ini")
    ),
)

@task
@needs(["minilib", "generate_setup", "setuptools.command.sdist"])
def sdist():
    pass

@task
@needs(["minilib", "generate_setup", "setuptools.command.bdist_egg"])
def bdist_egg():
    pass

@task
def required():
    """Install the required packages.

    Installs the requirements set in requirements.txt."""
    pip = path("bin/pip")
    if not pip.exists():
        sh('%s install -E tg2env -r normal-reqs.txt --extra-index-url=http://www.turbogears.org/2.0/downloads/current/index' % pip)
    call_pavement('pavement.py', 'develop')

@task
def start():
    """Starts Moksha on localhost port 8080 for development.

    You can change the port and allow remote connections by setting
    server.port or server.address on the command line::

        paver server.address=your.ip.address server.port=8000 start

    FIXME:
        - Get the loggers to work.
    """
    from paste.deploy import loadapp, loadserver
    from moksha.config.environment import load_environment
    from moksha.config.middleware import make_app
    ini = 'config:' + path('development.ini').abspath()
    wsgi_app = loadapp(ini)
    serve = loadserver(ini)
    serve(wsgi_app)

@task
def clean():
    data_path = path("devdata.db")
    data_path.unlink()

@task
def prod_server():
    """ Freezes our production requirements """
    sh("bin/pip freeze -r requirements.txt production/requirements.txt")

def _apply_header_if_necessary(f, header, first_line, last_line):
    data = f.bytes()
    if data.startswith(header):
        debug("File is already tagged")
        return
    debug("Tagging %s", f)
    if data.startswith(first_line):
        pos = data.find(last_line) + len(last_line)
        data = data[pos:]
    data = header + data
    f.write_bytes(data)

@task
def relicense():
    cwd = path('.')
    info("Re-licesning text")
    for extension, comment_marker in options.extensions:
        hlines = [comment_marker + " " + line for line in HEADER.split("\n")]
        header = "\n".join(hlines) + "\n\n"
        first_line = hlines[0]
        last_line = hlines[-1]
        for f in cwd.walkfiles("*.%s" % extension):
            exclude = False
            for pattern in options.exclude:
                if f.startswith(pattern):
                    exclude=True
                    break
            if exclude:
                continue
            info("Re-licensing %s" %  f)
            tmp = file(f, 'r')
            data = tmp.read()
            tmp.close()
            data = data.replace(OLDHEADER, HEADER)
            out = file(f, 'w')
            out.write(data)
            out.close()

@task
def license():
    """Tags the appropriate files with the license text."""
    cwd = path(".")
    info("Tagging license text")
    for extension, comment_marker in options.extensions:
        hlines = [comment_marker + " " + line for line in HEADER.split("\n")]
        header = "\n".join(hlines) + "\n\n"
        first_line = hlines[0]
        last_line = hlines[-1]
        for f in cwd.walkfiles("*.%s" % extension):
            exclude = False
            for pattern in options.exclude:
                if f.startswith(pattern):
                    exclude=True
                    break
            if exclude:
                continue
            _apply_header_if_necessary(f, header, first_line, last_line)

@task
def test():
    print "Running Moksha test suite..."
    sh('nosetests')

@task
def reinstall():
    print "Removing existing Moksha install"
    sh('rm -fr dist/')
    sh('python setup.py sdist --format=bztar')
    sh('mv dist/* ~/rpmbuild/SOURCES/')
    sh('cp moksha.spec ~/rpmbuild/SPECS/')
    sh('rpmbuild -ba ~/rpmbuild/SPECS/moksha.spec')
    sh('sudo rpm -e --nodeps moksha{,-doc,-server}', ignore_error=True)
    sh('sudo rpm -ivh ~/rpmbuild/RPMS/noarch/moksha{,-doc,-server}-%s-1.*noarch.rpm' % options.version.number)

@task
def restart_httpd():
    sh('sudo /sbin/service httpd restart')
    sh('curl http://localhost/')

@task
def restart_hub():
    sh('sudo /sbin/service moksha-hub restart')

@task
def restart_orbited():
    sh('sudo /sbin/service orbited restart')

@task
@cmdopts([
    ('distro=', 'd', 'Distribution to build for'),
    ('arch=', 'a', 'Architecture to build'),
])
def smock(options):
    """ Use smock.pl to rebuild everything in ~/rpmbuild/SRPMS """
    arches = getattr(options, 'arch', 'i386 x86_64').split()
    distros = getattr(options, 'distro',
                     'epel-5 fedora-11 fedora-rawhide fedora-10').split()
    for distro in distros:
        for arch in arches:
            sh('~/smock.pl --arch=%s --distro=%s ~/rpmbuild/SRPMS/*.rpm' % (
               arch, distro))


@task
@needs(['paver.doctools.html'])
def html():
    pass

@task
@needs(['reinstall', 'test', 'restart_httpd', 'restart_hub', 'restart_orbited'])
def all():
    pass
magic = all
