anybox.recipe.sysdeps
=====================

.. contents::

This is a simple and stupid buildout recipe to check system requirements.
It is primarily intended to check dependencies on Linux and MacOsX but any help to make
it work on Windows will be integrated.

Recipe options:
~~~~~~~~~~~~~~~

**deps**: list all the required system package names and the corresponding command
line to check the requirement.

Example buildout:
~~~~~~~~~~~~~~~~~
::

    [buildout]
    parts = sysdeps

    [sysdeps]
    recipe = anybox.recipe.sysdeps
    deps = PostgreSQL: which pg_dump
           Redis:      which redis-server
           php5-mysql: dpkg -l php5-mysql


If redis-server is not available, you will get an error while running the
buildout, telling you to install Redis.
You can use any command line to check whether the package is installed or not.

Contribute
~~~~~~~~~~
The primary branch is here:

- Code repository: https://bitbucket.org/anybox/anybox.recipe.sysdeps/

