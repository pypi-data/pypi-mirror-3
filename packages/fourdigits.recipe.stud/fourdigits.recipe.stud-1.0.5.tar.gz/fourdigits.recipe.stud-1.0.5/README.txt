
.. contents::

Supported options
=================

This recipe supports the following options:

url
    URL pointing to the ``stud`` compressed archive. By default it uses:
    https://github.com/bumptech/stud/tarball/master

target
    Target can be one of the following:
    linux22, linux24, linux24e linux24eold, linux26, solaris, freebsd,
    openbsd, generic.

cpu
    CPU can be one of the following: i686, i586, ultrasparc, generic.


Example usage
=============

To use this recipe, just create a part for it and define the ``recipe``
parameter::

    [buildout]
    parts =
        ...
        stud

    [stud]
    recipe = fourdigits.recipe.stud

This will configure the default options for ``url``, ``target``,
``cpu`` and ``livevversion``. If you like or need to you can override these parameters, e.g.::

    [haproxy]
    recipe = foudigits.recipe.stud
    url = https://github.com/bumptech/stud/tarball/master
    target = linux26
    cpu = i686
    libevversion = 4.04


Reporting bugs or asking questions
==================================

https://github.com/kingel/fourdigits.recipe.stud/issues

Code repository
===============

https://github.com/kingel/fourdigits.recipe.stud
