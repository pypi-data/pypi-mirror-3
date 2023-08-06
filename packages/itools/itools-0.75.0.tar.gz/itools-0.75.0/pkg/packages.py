# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@supinfo.com>
# Copyright (C) 2008-2010 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2010 Hervé Cauwelier <herve@oursours.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from operator import itemgetter
from os import sep
from os.path import join, split
from sys import path as python_path

# Import from itools
from itools.fs import vfs
from metadata import get_package_version, parse_setupconf, PKGINFOFile
from packages_db import PACKAGES_DB


def get_setupconf(package):
    setupconf = join(package, "setup.conf")
    if vfs.is_file(setupconf):
        return parse_setupconf(package)
    return None


def get_egginfo(egginfo):
    if vfs.is_folder(egginfo) and egginfo.endswith('.egg-info'):
        egginfo = join(egginfo, 'PKG-INFO')
    elif not (vfs.is_file(egginfo) and egginfo.endswith('.egg-info')):
        return None

    handler = PKGINFOFile(egginfo)
    handler.load_state()
    attrs = handler.attrs
    return attrs


def get_minpackage(dir):
    package = split(dir)[1]
    path = join(dir, '__init__.py')
    if vfs.exists(path) and vfs.is_file(path):
        return {'name': package, 'version': get_package_version(package)}
    return None


def packages_infos(module_name=None):
    # find the site-packages absolute path
    sites = set([])
    for dir in python_path:
        if 'site-packages' in dir:
            dir = dir.split(sep)
            sites.add(sep.join(dir[:dir.index('site-packages')+1]))

    packages = {}
    recorded_packages = []
    name_mask = set()
    version_mask = set()
    module_mask = set()

    def add_package(site, package):
        if site in packages:
            packages[site].append(package)
        else:
            packages[site] = [package]

    for site in sites:
        for db_name, db_version, db_module in PACKAGES_DB:
            db_version = db_version.replace('*', '')
            for egg_info in vfs.get_names(site):
                egg_split = egg_info[:-len('.egg-info')].split('-')
                egg_name = egg_split[0]
                if egg_name != db_name:
                    continue
                egg_version = egg_split[1]
                if not egg_version.startswith(db_version):
                    continue
                data = get_egginfo(join(site, egg_info))
                if module_name and module_name != data['name']:
                    continue
                data['module'] = db_module
                add_package(site, (data['name'], data, 'E'))
                recorded_packages.append(data['name'])
                name_mask.add(db_name)
                version_mask.add(egg_version)
                module_mask.add(db_module)
                break

    # TODO understand .egg -maybe by using setuptools-
    for site in sites:
        for package in vfs.get_names(site):
            if package in module_mask:
                continue

            if (package.endswith('.egg-info')):
                pkg_split = package.split('-')
                if pkg_split[0] in name_mask:
                    continue
                if pkg_split[1] in version_mask:
                    continue
                # Why the first?
                data = get_egginfo(join(site, package))
                if (data['name'] in recorded_packages or
                   (module_name and data['name'] != module_name)):
                    continue
                add_package(site, (data['name'], data, 'E'))
                recorded_packages.append(data['name'])
                continue
            elif module_name and module_name != package:
                continue

            data = get_setupconf(join(site, package))
            if data and data['name'] not in recorded_packages:
                add_package(site, (data['name'], data, 'S'))
                recorded_packages.append(data['name'])
                continue

            data = get_minpackage(join(site, package))
            if data and data['name'] not in recorded_packages:
                add_package(site, (data['name'], data, 'M'))
                recorded_packages.append(data['name'])
                continue


    for site in packages:
        packages[site].sort(cmp=lambda a, b: cmp(a.upper(),b.upper()),
                      key=itemgetter(0))
        yield (site, packages[site])
