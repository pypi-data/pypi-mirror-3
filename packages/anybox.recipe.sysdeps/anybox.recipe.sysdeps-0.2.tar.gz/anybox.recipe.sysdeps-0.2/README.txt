anybox.recipe.sysdeps
=====================

.. contents::

This is a buildout recipe to check system dependencies.
It is primarily intended to check deps on Linux and MacOsX but any help to make
it work on Windows will be integrated.

Recipe options:
~~~~~~~~~~~~~~~

**bin**: list all the required executables and the corresponding needed system
package.

Example buildout:
~~~~~~~~~~~~~~~~~
::

    [buildout]
    parts = sysdeps

    [sysdeps]
    recipe = anybox.recipe.sysdeps
    bin = pg_dump:PostgreSQL
          pg_restore:PostgreSQL
          redis-server:Redis


If redis-server is not available, you will get an error while running the
buildout, telling you to install Redis.

Contribute
~~~~~~~~~~
The primary branch is on the launchpad:

- Code repository: https://code.launchpad.net/~anybox/+junk/anybox.recipe.sysdeps

