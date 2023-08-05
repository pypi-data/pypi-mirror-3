=================================
The ``runscript`` Buildout Recipe
=================================

Some software packages are not easily installed using established build patterns, such
as "configure, make, make install". In those cases you want to be able to use
arbitrary scripts to build a particular part. This recipe provides a simple
implementation to run a Python callable for each installing and updating a
part.

    >>> import os
    >>> import z3c.recipe.runscript.tests
    >>> scriptFilename = os.path.join(
    ...     os.path.dirname(z3c.recipe.runscript.tests.__file__), 'fooscripts.py')

Let's create a sample buildout to install it:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = z3c.recipe.runscript
    ... install-script = %s:installFoo
    ... """ %scriptFilename)

The ``install-script`` option specifies the module and the function to call
during the part installation. The function takes the local and buildout
options as arguments. See ``tests/fooscripts.py`` for details.

When running buildout, the ``installFoo()`` function is called:

    >>> print system('bin/buildout')
    Installing foo.
    Now executing ``installFoo()``

If we run the buildout again, the update method will be called, but since we
did not specify any, nothing happens:

    >>> print system('bin/buildout')
    Updating foo.

Let's now specify the update script as well, causing the ``updateFoo()``
function to be called:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = foo
    ...
    ... [foo]
    ... recipe = z3c.recipe.runscript
    ... install-script = %s:installFoo
    ... update-script = %s:updateFoo
    ... """ %(scriptFilename, scriptFilename))

But after a change like that, parts will be uninstalled and reinstalled:

    >>> print system('bin/buildout')
    Uninstalling foo.
    Installing foo.
    Now executing ``installFoo()``

Only now we can update the part:

    >>> print system('bin/buildout')
    Updating foo.
    Now executing ``updateFoo()``

And that's it.
