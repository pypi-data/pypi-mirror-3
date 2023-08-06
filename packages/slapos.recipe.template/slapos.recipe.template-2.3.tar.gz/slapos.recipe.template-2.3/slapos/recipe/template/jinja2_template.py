##############################################################################
#
# Copyright (c) 2012 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import errno
import os
import json
import zc.buildout
from jinja2 import Template, StrictUndefined
from contextlib import contextmanager

@contextmanager
def umask(mask):
    original = os.umask(mask)
    try:
        yield original
    finally:
        os.umask(original)

def getKey(expression, buildout, _,options):
    section, entry = expression.split(':')
    if section:
        return buildout[section][entry]
    else:
        return options[entry]

def getJsonKey(expression, buildout, _, __):
    return json.loads(getKey(expression, buildout, _, __))

EXPRESSION_HANDLER = {
    'raw': (lambda expression, _, __, ___: expression),
    'key': getKey,
    'json': (lambda expression, _, __, ___: json.loads(expression)),
    'jsonkey': getJsonKey,
    'import': (lambda expression, _, __, ___: __import__(expression)),
    'section': (lambda expression, buildout, _, __: dict(buildout[expression])),
}

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.template = zc.buildout.download.Download(
                buildout['buildout'],
                hash_name=True,
            )(
                options['template'],
                md5sum=options.get('md5sum'),
            )[0]
        self.rendered = options['rendered']
        self.extension_list = [x for x in (y.strip() for y in options.get('extensions', '').split()) if x]
        self.context = context = {}
        for line in options.get('context').splitlines(False):
            if not line:
                continue
            expression_type, variable_name, expression = line.split(None, 2)
            if variable_name in context:
                raise ValueError('Duplicate context entry %r' % (
                    variable_name, ))
            context[variable_name] = EXPRESSION_HANDLER[expression_type](
                expression, buildout, name, options)
        if 'umask' in options:
            self.umask = int(options['umask'], 8)
        else:
            self.umask = os.umask(0)
            os.umask(self.umask)

    def install(self):
        if os.path.lexists(self.rendered):
            # Unlink any existing file, so umask is always applied.
            os.unlink(self.rendered)
        with umask(self.umask):
            outdir = os.path.dirname(self.rendered)
            if outdir and not os.path.exists(outdir):
                os.makedirs(outdir)
            with open(self.rendered, 'w') as out:
                out.write(Template(
                        open(self.template).read(),
                        extensions=self.extension_list,
                        undefined=StrictUndefined,
                    ).render(
                        **self.context
                    )
                )
        return self.rendered

    update = install

