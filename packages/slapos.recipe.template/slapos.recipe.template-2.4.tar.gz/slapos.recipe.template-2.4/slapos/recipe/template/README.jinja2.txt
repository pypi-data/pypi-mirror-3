Jinja2 usage
============

Getting started
---------------

Example buildout demonstrating some types::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context =
    ...     key     bar          section:key
    ...     key     recipe       :recipe
    ...     raw     knight       Ni !
    ...     json    words        ["Peng", "Neee-wom"]
    ...     jsonkey later        section:later-words
    ...     import  json_module  json
    ...     section param_dict   parameter-collection
    ...
    ... [parameter-collection]
    ... foo = 1
    ... bar = bar
    ...
    ... [section]
    ... key = value
    ... later-words = "Ekke Ekke Ekke Ekke Ptangya Ziiinnggggggg Ni!"
    ... ''')

And according Jinja2 template (kept simple, control structures are possible)::

    >>> write('foo.in',
    ...     '{{bar}}\n'
    ...     'Knights who say "{{knight}}" also protect {{ words | join(", ") }}.\n'
    ...     'They later say {{later}}\n'
    ...     '${this:is_literal}\n'
    ...     '${foo:{{bar}}}\n'
    ...     'swallow: {{ json_module.dumps(("african", "european")) }}\n'
    ...     'parameters from section: {{ param_dict | dictsort }}\n'
    ...     'Rendered with {{recipe}}'
    ... )

We run buildout::

    >>> print system(join('bin', 'buildout')),
    Installing template.

And the template has been rendered::

    >>> cat('foo')
    value
    Knights who say "Ni !" also protect Peng, Neee-wom.
    They later say Ekke Ekke Ekke Ekke Ptangya Ziiinnggggggg Ni!
    ${this:is_literal}
    ${foo:value}
    swallow: ["african", "european"]
    parameters from section: [('bar', 'bar'), ('foo', '1')]
    Rendered with slapos.recipe.template:jinja2

Parameters
----------

Mandatory:

``template``
  Template url/path, as accepted by zc.buildout.download.Download.__call__ .

``rendered``
  Where rendered template should be stored.

Optional:

``context``
  Jinja2 context specification, one variable per line, with 3
  whitespace-separated parts: type, name and expression. Available types are
  described below. "name" is the variable name to declare. Expression semantic
  varies depending on the type.

  Available types:

  ``raw``
    Immediate literal string.

  ``json``
    Immediate json-encoded string.

  ``key``
    Indirect literal string.

  ``jsonkey``
    Indirect json-encoded string.

  ``import``
    Import a python module.

  ``section``
    Make a whole buildout section available to template, as a dictionary.

  Indirection targets are specified as: [section]:key .
  It is possible to use buildout's buit-in variable replacement instead instead
  of ``key`` or ``jsonkey`` types, but keep in mind that different lines are
  different variables for this recipe. It might be what you want (factorising
  context chunk declarations), otherwise you should use indirect types.

``md5sum``
  Template's MD5, for file integrity checking. By default, no integrity check
  is done.

``umask``
  Umask, in octal notation (no need for 0-prefix), to create output file with.
  Defaults to system's umask at the time recipe is instanciated.

``extensions``
  Jinja2 extensions to enable when rendering the template,
  whitespace-separated. By default, none is loaded.

FAQ
---

Q: How do I generate ${foo:bar} where foo comes from a variable ?

A: ``{{ '${' ~ foo_var ~ ':bar}' }}``
   This is required as jinja2 fails parsing "${{{ foo_var }}:bar}". Though,
   jinja2 succeeds at parsing "${foo:{{ bar_var }}}" so this trick isn't
   needed for that case.

Use jinja2 extensions
~~~~~~~~~~~~~~~~~~~~~

    >>> write('foo.in',
    ... '''{% set foo = ['foo'] -%}
    ... {% do foo.append(bar) -%}
    ... {{ foo | join(', ') }}''')
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar buildout:parts
    ... # We don't actually use all those extensions in this minimal example.
    ... extensions = jinja2.ext.do jinja2.ext.loopcontrols
    ...   jinja2.ext.with_
    ... ''')
    >>> print system(join('bin', 'buildout')),
    Uninstalling template.
    Installing template.

    >>> cat('foo')
    foo, template

Check file integrity
~~~~~~~~~~~~~~~~~~~~

Compute template's MD5 sum::

    >>> write('foo.in', '{{bar}}')
    >>> import md5
    >>> md5sum = md5.new(open('foo.in', 'r').read()).hexdigest()
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar buildout:parts
    ... md5sum = ''' + md5sum + '''
    ... ''')
    >>> print system(join('bin', 'buildout')),
    Uninstalling template.
    Installing template.

    >>> cat('foo')
    template

If the md5sum doesn't match, the buildout fail::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar buildout:parts
    ... md5sum = 0123456789abcdef0123456789abcdef
    ... ''')
    >>> print system(join('bin', 'buildout')),
    While:
      Installing.
      Getting section template.
      Initializing part template.
    Error: MD5 checksum mismatch for local resource at 'foo.in'.


Specify filesystem permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify the umask for rendered file::

    >>> write('template.in', '{{bar}}')
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar buildout:parts
    ... umask = 570
    ... ''')
    >>> print system(join('bin', 'buildout')),
    Uninstalling template.
    Installing template.

And the generated file with have the right permissions::

    >>> import stat
    >>> import os
    >>> print oct(stat.S_IMODE(os.stat('foo').st_mode))
    0206

Section dependency
------------------

You can use other part of buildout in the template. This way this parts
will be installed as dependency::

    >>> write('foo.in', '{{bar}}')
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar dependency:foobar
    ...
    ... [dependency]
    ... foobar = dependency content
    ... recipe = zc.buildout:debug
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Uninstalling template.
    Installing dependency.
      foobar='dependency content'
      recipe='zc.buildout:debug'
    Installing template.

This way you can get options which are computed in the ``__init__`` of
the dependent recipe.

Let's create a sample recipe modifying its option dict::

    >>> write('setup.py',
    ... '''
    ... from setuptools import setup
    ...
    ... setup(name='samplerecipe',
    ...       entry_points = {
    ...           'zc.buildout': [
    ...                'default = main:Recipe',
    ...           ],
    ...       }
    ...      )
    ... ''')
    >>> write('main.py',
    ... '''
    ... class Recipe(object):
    ...
    ...     def __init__(self, buildout, name, options):
    ...         options['data'] = 'foobar'
    ...
    ...     def install(self):
    ...         return []
    ... ''')

Let's just use ``buildout.cfg`` using this egg::

    >>> write('foo.in', '{{bar}}')
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = .
    ... parts = template
    ...
    ... [template]
    ... recipe = slapos.recipe.template:jinja2
    ... template = foo.in
    ... rendered = foo
    ... context = key bar sample:data
    ...
    ... [sample]
    ... recipe = samplerecipe
    ... ''')
    >>> print system(join('bin', 'buildout')),
    Develop: ...
    Uninstalling template.
    Uninstalling dependency.
    Installing sample.
    Installing template.
    >>> cat('foo')
    foobar

