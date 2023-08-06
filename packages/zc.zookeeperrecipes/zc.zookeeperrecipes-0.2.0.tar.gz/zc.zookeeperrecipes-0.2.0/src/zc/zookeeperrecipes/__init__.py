##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import datetime
import logging
import os
import re
import signal
import textwrap
import zc.buildout
import zc.zk

logger = logging.getLogger(__name__)

def timestamp():
    return datetime.datetime.now().isoformat()

timestamped = re.compile(r'(.+)\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+$').match

class DevTree:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        if 'zookeeper' not in options:
            options['zookeeper'] = '127.0.0.1:2181'

        if 'import-file' in options:
            options['import-text'] = open(os.path.join(
                buildout['buildout']['directory'],
                options['import-file'])).read()

        options['location'] = location = os.path.join(
            buildout['buildout']['parts-directory'], name)

        if 'effective-path' not in options:
            path = options.get('path', name)
            if not path.startswith('/'):
                path = '/' + path
            options['path'] = path

            if os.path.exists(location):
                with open(location) as f:
                    epath = f.read()
                    m = timestamped(epath)
                    if m and m.group(1) == path:
                        options['effective-path'] = epath
                    else:
                        options['effective-path'] = path + timestamp()
            else:
                options['effective-path'] = path + timestamp()

        if not options.get('clean', 'auto') in ('auto', 'yes', 'no'):
            raise zc.buildout.UserError(
                'clean must be one of "auto", "yes", or "no"')

        # helper scripts
        prefix = options.get('helper-scripts')
        if prefix:
            def add_section(name, options):
                buildout._raw[name] = options
                buildout[name]

            zk = options['zookeeper']+options['effective-path']
            if prefix+'scripts' not in buildout:
                add_section(prefix+'scripts', dict(
                    recipe = 'zc.recipe.egg',
                    eggs = 'zc.zk [static]',
                    scripts = ('zookeeper_export=%(prefix)sexport '
                               'zookeeper_import=%(prefix)simport'
                               % dict(prefix=prefix)
                               ),
                    arguments = '[%r] + sys.argv[1:]' % zk,
                    ))
            if prefix+'print' not in buildout:
                add_section(prefix+'print', dict(
                    recipe = 'zc.recipe.egg',
                    eggs = 'zc.zk [static]',
                    scripts = 'zookeeper_export=%sprint' % prefix,
                    arguments = '[%r, "-e"] + sys.argv[1:]' % zk,
                    ))
            if prefix+'port' not in buildout:
                add_section(prefix+'port', dict(
                    recipe = 'zc.recipe.egg',
                    eggs = 'zc.zk [static]',
                    scripts = prefix+'port',
                    initialization=zkport % zk,
                    **{'entry-points': prefix+'port=time:time'}
                    ))


    def install(self):
        options = self.options
        connection = options['zookeeper']
        zk = zc.zk.ZooKeeper(connection)
        location = options['location']
        path = options['effective-path']
        base, name = path.rsplit('/', 1)
        if base:
            zk.create_recursive(base, '', zc.zk.OPEN_ACL_UNSAFE)
        zk.import_tree(
            '/'+name+'\n  buildout:location = %r\n  ' % location +
            textwrap.dedent(
                self.options.get('import-text', '')
                ).replace('\n', '\n  '),
            base, trim=True)

        with open(location, 'w') as f:
            f.write(path)

        clean = options.get('clean', 'auto')
        if (clean == 'yes' or
            (clean == 'auto' and (
                connection.startswith('localhost:')
                or
                connection.startswith('127.')
                )
             )
            ):
            self.clean(zk)

        return ()

    update = install

    def clean(self, zk):
        for name in zk.get_children('/'):
            if name == 'zookeeper':
                continue
            self._clean(zk, '/'+name)

    def _clean(self, zk, path):
        location = zk.get_properties(path).get('buildout:location')
        if location is not None:
            if not os.path.exists(location) or readfile(location) != path:
                pids = []
                for spath in zk.walk(path):
                    if spath != path:
                        if zk.is_ephemeral(spath):
                            pid = zk.get_properties(spath).get('pid')
                            if pid:
                                pids.append(pid)
                zk.delete_recursive(path, force=True)
                for pid in pids:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except OSError:
                        logger.warn('Failed to kill')
        else:
            for name in zk.get_children(path):
                self._clean(zk, path + '/' + name)

def readfile(path):
    with open(path) as f:
        return f.read()

zkport = """
args = sys.argv[1:]
import zc.zk
zk = zc.zk.ZK(%r)
path = args.pop(0)
if path[-1:] == '/':
    path += 'providers'
child = zk.get_children(path)[0]
if args:
    [prop] = args
    child = zk.get_properties(path + '/' + child)[prop]
print child.split(':')[-1]
zk.close()
"""
