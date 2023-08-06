# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@supinfo.com>
# Copyright (C) 2008, 2010 Hervé Cauwelier <herve@oursours.net>
# Copyright (C) 2008-2009 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2009 Aurélien Ansel <camumus@gmail.com>
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
from os.path import join
from rfc822 import Message

# Import from itools
from itools.datatypes import String, LanguageTag, Tokens
from itools.handlers import ConfigFile, TextFile, register_handler_class
from itools.fs import vfs


class SetupFile(ConfigFile):
    """abstract a setup.conf file
    """

    schema = {
        'name': String(default=''),
        'title': String(default=''),
        'url': String(default=''),
        'author_name': String(default=''),
        'author_email': String(default=''),
        'license': String(default=''),
        'description': String(default=''),
        'packages': Tokens,
        'requires': Tokens,
        'provides': Tokens,
        'scripts': Tokens,
        'source_language': LanguageTag(default=('en', 'EN')),
        'target_languages': Tokens(default=(('en', 'EN'),))
    }



class RFC822File(TextFile):
    """ holds a rfc822 Message """

    attrs = {}
    message = None

    list_types = (type([]), type(()))
    str_types = (type(''),)

    def new(self, **kw):
        if 'attrs' in kw.keys():
            self.set_attrs(kw['attrs'])


    def _load_state_from_file(self, file):
        self.attrs = {}
        self.message = Message(file)
        for k in self.message.keys():
            if self.schema is None:
                if len(self.message.getheaders(k)) == 1:
                    self.attrs[k] = self.message.getheader(k)
                else:
                    self.attrs[k] = self.message.getheaders(k)
            elif k in self.schema:
                if issubclass(self.schema[k], String):
                    self.attrs[k] = self.message.getheader(k)
                elif issubclass(self.schema[k], Tokens):
                    self.attrs[k] = self.message.getheaders(k)


    def to_str(self):
        data = ''
        list_types = (type([]), type(()))
        str_types = (type(''),)
        for key, val in self.attrs.items():
            if type(val) in str_types:
                data += '%s: %s\n' % (key, val)
            elif type(val) in list_types:
                # a new line for each item of the list
                for v in val:
                    data += '%s: %s\n' % (key, v)

        return data


    #######################################################################
    # API
    #######################################################################
    def set_attrs(self, attrs):
        # Check types of values
        type_error_msg = 'One of the given values is not compatible'
        for key, val in attrs.items():
            if type(val) in self.list_types:
                for v in val:
                    if type(v) not in self.str_types:
                        raise TypeError, type_error_msg
            elif self.schema is not None and key not in self.schema:
                del attrs[key]

        # Now attrs is sure
        self.attrs = attrs
        self.set_changed()


    def get_attrs(self):
        if self.schema is not None:
            for key in self.schema:
                if key not in self.attrs:
                    self.attrs[key] = self.schema[key].get_default()
        return self.attrs



class PKGINFOFile(RFC822File):

    class_mimetypes = ['text/x-egg-info']

    schema = {
        'metadata-version': String(default=''),
        'name': String(default=''),
        'version': String(default=''),
        'summary': String(default=''),
        'author-email': String(default=''),
        'license': String(default=''),
        'download-url': String(default=''),

        # Optional
        'description': String(default=''),
        'keywords': Tokens,
        'home-page': String(default=''),
        'author': String(default=''),
        'platform': String(default=''),
        'supported-platform': String(default=''),
        'classifiers': Tokens,
        'requires': Tokens,
        'provides': Tokens,
        'obsoletes': Tokens,
    }


register_handler_class(PKGINFOFile)


def parse_setupconf(package_dir):
    """Return a dict containing information from setup.conf in a itools package
    plus the version of the package
    """
    attributes = {}
    if not vfs.is_folder(package_dir):
        return attributes
    if not vfs.exists(join(package_dir, "setup.conf")):
        return attributes
    config = SetupFile(join(package_dir, "setup.conf"))
    for attribute in config.schema:
        attributes[attribute] = config.get_value(attribute)
    if vfs.exists(join(package_dir, "version.txt")):
        attributes['version'] = open(join(package_dir, "version.txt")).read()
    else:
        attributes['version'] = get_package_version(attributes['name'])
    return attributes


def get_package_version(package_name):
    try:
        mod = __import__(package_name)
    except ImportError:
        return '?'

    for name in ['Version', '__version__', 'version']:
        version = getattr(mod, name, None)
        if version is not None:
            if hasattr(version,'__call__'):
                return version()
            return version
    return '?'
