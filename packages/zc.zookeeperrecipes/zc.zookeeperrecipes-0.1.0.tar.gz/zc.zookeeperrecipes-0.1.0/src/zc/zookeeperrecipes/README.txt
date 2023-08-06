=================
ZooKeeper Recipes
=================

devtree
=======

The devtree recipe sets up temporary ZooKeeper tree for a buildout::

  [myproject]
  recipe = zc.zookeeperrecipes:devtree
  import-file = tree.txt

.. -> conf

    *** Basics, default path,  ***

    >>> def write(name, text):
    ...     with open(name, 'w') as f: f.write(text)

    >>> write('tree.txt', """
    ... x=1
    ... type = 'foo'
    ... /a
    ...    /b
    ... /c
    ... """)

    >>> import ConfigParser, StringIO, os
    >>> from zc.zookeeperrecipes import DevTree

    >>> here = os.getcwd()
    >>> buildoutbuildout = {
    ...     'directory': here,
    ...     'parts-directory': os.path.join(here, 'parts'),
    ...     }

    >>> def buildout():
    ...     parser = ConfigParser.RawConfigParser()
    ...     parser.readfp(StringIO.StringIO(conf))
    ...     buildout = dict((name, dict(parser.items(name)))
    ...                     for name in parser.sections())
    ...     [name] = buildout.keys()
    ...     buildout['buildout'] = buildoutbuildout
    ...     options = buildout[name]
    ...     recipe = DevTree(buildout, name, options)
    ...     return recipe, options


    >>> import zc.zookeeperrecipes, mock
    >>> with mock.patch('zc.zookeeperrecipes.timestamp') as ts:
    ...     ts.return_value = '2012-01-26T14:50:14.864772'
    ...     recipe, options = buildout()


    >>> from pprint import pprint
    >>> pprint(options)
    {'effective-path': '/myproject2012-01-26T14:50:14.864772',
     'import-file': 'tree.txt',
     'import-text': "\nx=1\ntype = 'foo'\n/a\n   /b\n/c\n",
     'location': '/testdirectory/parts/myproject',
     'path': '/myproject',
     'recipe': 'zc.zookeeperrecipes:devtree'}

    >>> recipe.install()
    ()

    >>> def cat(*path):
    ...     with open(os.path.join(*path)) as f:
    ...          return f.read()

    >>> cat('parts', 'myproject')
    '/myproject2012-01-26T14:50:14.864772'

  *** Test node name is persistent ***

  Updating doesn't change the name:

    >>> recipe, options = buildout()
    >>> recipe.update()
    ()
    >>> options['effective-path'] == '/myproject2012-01-26T14:50:14.864772'
    True
    >>> cat('parts', 'myproject')
    '/myproject2012-01-26T14:50:14.864772'

    >>> import zc.zk
    >>> zk = zc.zk.ZooKeeper('127.0.0.1:2181')
    >>> zk.print_tree()
    /myproject2012-01-26T14:50:14.864772 : foo
      buildout:location = u'/testdirectory/parts/myproject'
      x = 1
      /a
        /b
      /c

  *** Test updating tree source ***

  If there are changes, we see them

    >>> write('tree.txt', """
    ... /a
    ...   /d
    ... /c
    ... """)

    >>> buildout()[0].install()
    ()
    >>> zk.print_tree()
    /myproject2012-01-26T14:50:14.864772
      buildout:location = u'/testdirectory/parts/myproject'
      /a
        /d
      /c

  Now, if there are ephemeral nodes:

    >>> with mock.patch('os.getpid') as getpid:
    ...     getpid.return_value = 42
    ...     zk.register_server('/myproject2012-01-26T14:50:14.864772/a/d',
    ...                        'x:y')

    >>> write('tree.txt', """
    ... /a
    ...   /b
    ... /c
    ... """)

    >>> buildout()[0].install() # doctest: +NORMALIZE_WHITESPACE
    Not deleting /myproject2012-01-26T14:50:14.864772/a/d/x:y
     because it's ephemeral.
    /myproject2012-01-26T14:50:14.864772/a/d
     not deleted due to ephemeral descendent.
    ()

    >>> zk.print_tree()
    /myproject2012-01-26T14:50:14.864772
      buildout:location = u'/testdirectory/parts/myproject'
      /a
        /b
        /d
          /x:y
            pid = 42
      /c

  The ephemeral node, and the node containing it is left, but a
  warning is issued.

  *** Cleanup w different part name ***

  Now, let's change out buildout to use a different part name:

    >>> conf = """
    ... [myproj]
    ... recipe = zc.zookeeperrecipes:devtree
    ... import-file = tree.txt
    ... """

    >>> os.remove(os.path.join('parts', 'myproject'))

  Now, when we rerun the buildout, the old tree will get cleaned up:

    >>> import signal
    >>> with mock.patch('os.kill') as kill:
    ...     with mock.patch('zc.zookeeperrecipes.timestamp') as ts:
    ...         ts.return_value = '2012-01-26T14:50:15.864772'
    ...         recipe, options = buildout()
    ...     recipe.install()
    ...     kill.assert_called_with(42, signal.SIGTERM)
    ()

    >>> pprint(options)
    {'effective-path': '/myproj2012-01-26T14:50:15.864772',
     'import-file': 'tree.txt',
     'import-text': '\n/a\n  /b\n/c\n',
     'location': '/testdirectory/parts/myproj',
     'path': '/myproj',
     'recipe': 'zc.zookeeperrecipes:devtree'}

    >>> with mock.patch('os.getpid') as getpid:
    ...     getpid.return_value = 42
    ...     zk.register_server('/myproj2012-01-26T14:50:15.864772/a/b',
    ...                        'x:y')

    >>> zk.print_tree()
    /myproj2012-01-26T14:50:15.864772
      buildout:location = u'/testdirectory/parts/myproj'
      /a
        /b
          /x:y
            pid = 42
      /c


  *** Cleanup w different path and explicit path, and creation of base nodes ***

    >>> conf = """
    ... [myproj]
    ... recipe = zc.zookeeperrecipes:devtree
    ... import-file = tree.txt
    ... path = /ztest/path
    ... """

    >>> with mock.patch('os.kill') as kill:
    ...     with mock.patch('zc.zookeeperrecipes.timestamp') as ts:
    ...         ts.return_value = '2012-01-26T14:50:16.864772'
    ...         recipe, options = buildout()
    ...     recipe.install()
    ...     kill.assert_called_with(42, signal.SIGTERM)
    ()

    >>> pprint(options)
    {'effective-path': '/ztest/path2012-01-26T14:50:16.864772',
     'import-file': 'tree.txt',
     'import-text': '\n/a\n  /b\n/c\n',
     'location': '/tmp/tmpZ3mohq/testdirectory/parts/myproj',
     'path': '/ztest/path',
     'recipe': 'zc.zookeeperrecipes:devtree'}

    >>> with mock.patch('os.getpid') as getpid:
    ...     getpid.return_value = 42
    ...     zk.register_server('/ztest/path2012-01-26T14:50:16.864772/a/b',
    ...                        'x:y')

    >>> zk.print_tree()
    /ztest
      /path2012-01-26T14:50:16.864772
        buildout:location = u'/tmp/tmpZ3mohq/testdirectory/parts/myproj'
        /a
          /b
            /x:y
              pid = 42
        /c

  *** explicit effective-path ***

  We can control the effective-path directly:

    >>> conf = """
    ... [myproj]
    ... recipe = zc.zookeeperrecipes:devtree
    ... effective-path = /my/path
    ... import-file = tree.txt
    ... """

  This time, we'll also check
  that kill fail handlers are handled properly.

    >>> with mock.patch('os.kill') as kill:
    ...     def noway(pid, sig):
    ...         raise OSError
    ...     kill.side_effect = noway
    ...     recipe, options = buildout()
    ...     recipe.install()
    ...     kill.assert_called_with(42, signal.SIGTERM)
    ()

    >>> pprint(options)
    {'effective-path': '/my/path',
     'import-file': 'tree.txt',
     'import-text': '\n/a\n  /b\n/c\n',
     'location': '/testdirectory/parts/myproj',
     'recipe': 'zc.zookeeperrecipes:devtree'}

    >>> zk.print_tree() # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    /my
      /path
        buildout:location = u'/tmp/tmpiKIi2U/testdirectory/parts/myproj'
        /a
          /b
        /c
    /ztest

    >>> zk.close()

  *** Non-local zookeeper no cleanup no/explicit import text ***

    **Note** because of the way zookeeper testing works, there's
    really only one zookeeper "server", so even though we're using a
    different connection string, we get the same db.

    >>> conf = """
    ... [myproj]
    ... recipe = zc.zookeeperrecipes:devtree
    ... effective-path = /my/path
    ... zookeeper = zookeeper.example.com:2181
    ... """

    >>> recipe, options = buildout()
    >>> recipe.install()
    ()

    >>> pprint(options)
    {'effective-path': '/my/path',
     'location': '/tmp/tmpUAkJkK/testdirectory/parts/myproj',
     'recipe': 'zc.zookeeperrecipes:devtree',
     'zookeeper': 'zookeeper.example.com:2181'}

    >>> zk = zc.zk.ZooKeeper('zookeeper.example.com:2181')
    >>> with mock.patch('os.getpid') as getpid:
    ...     getpid.return_value = 42
    ...     zk.register_server('/my/path', 'a:b')
    >>> zk.print_tree()
    /my
      /path
        buildout:location = u'/tmp/tmp2Qp4qX/testdirectory/parts/myproj'
        /a:b
          pid = 42
    /ztest

    >>> conf = """
    ... [myproj]
    ... recipe = zc.zookeeperrecipes:devtree
    ... import-text = /a
    ... zookeeper = zookeeper.example.com:2181
    ... path =
    ... """


    >>> with mock.patch('os.kill') as kill:
    ...     def noway(pid, sig):
    ...         print 'wtf killed'
    ...     kill.side_effect = noway
    ...     with mock.patch('zc.zookeeperrecipes.timestamp') as ts:
    ...         ts.return_value = '2012-01-26T14:50:24.864772'
    ...         recipe, options = buildout()
    ...     recipe.install()
    ()

    >>> zk.print_tree()
    /2012-01-26T14:50:24.864772
      buildout:location = u'/tmp/tmpxh1XPP/testdirectory/parts/myproj'
      /a
    /my
      /path
        buildout:location = u'/tmp/tmpxh1XPP/testdirectory/parts/myproj'
        /a:b
          pid = 42
    /ztest


In this example, we're creating a ZooKeeper tree at the path
``/myprojectYYYY-MM-DDTHH:MM:SS.SSSSSS`` with data imported from the
buildout-local file ``tree.txt``, where YYYY-MM-DDTHH:MM:SS.SSSSSS is
the ISO date-time when the node was created.

The ``tree`` recipe options are:

zookeeper
   Optional ZooKeeper connection string.

   It defaults to '127.0.0.1:2181'.

path
   Optional path at which to create the tree.

   If not provided, the part name is used, with a leading ``/`` added.

   When a ``devtree`` part is installed, a path is created at a path
   derived from the given (or implied) path by adding the current date
   and time to the path in ISO date-time format
   (YYYY-MM-DDTHH:MM:SS.SSSSSS).  The derived path is stored a file in
   the buildout parts directory with a name equal to the section name.

effective-path
   Optional path to be used as is.

   This option is normally computed by the recipe and is queryable
   from other recipes, but it may also be set explicitly.

import-file
   Optional import file.

   This is the name of a file containing tree-definition text. See the
   ``zc.zk`` documentation for information on the format of this file.

import-text
   Optional import text.

   Unfortunately, because of the way buildout parses configuration
   files, leading whitespace is stripped, making this option hard to
   specify.

Cleanup
-------

We don't want trees to accumulate indefinately.  When using a local
zookeeper (default), when the recipe is run, the entire tree is
scanned looking for nodes that have ``buildout:location`` properties
with paths that no-longer exist in the local file system paths that
contain different ZooKeeper paths.

If such nodes are found, then the nodes are removed and, if the nodes
had any ephemeral subnodes with pids, those pids are sent a SIGTERM
signal.

Change History
==============

0.1.0 (2011-02-02)
------------------

Initial release
