=======================================
 Barabash - A build scripting framework
=======================================

:WebSite: http://barabash.99k.org
:Download: http://pypi.python.org/pypi/barabash/
:Source: https://bitbucket.org/godfryd/barabash/src
:Mailing List: http://groups.google.com/group/barabash/
:Keywords: build, scripting, make alternative, scons alternative, cmake alternative
:Last updated: |today|

--

.. _barabash-synopsis:

Barabash is a build scripting framework.
It takes some concepts from `GNU make <http://www.gnu.org/software/make/>`_,
`CMake <http://www.cmake.org/>`_ and `SCons <http://www.scons.org/>`_.

Fundamental assumptions:

* dependencies like in *GNU make*
* coding recipies as Bash scripts as in *GNU make* but also as Python functions as in *SCons*
* Bash recipies behave as regular scripts in contrary to *GNU make*, i.e. no more line continuations with ``\``
* auto-clean, all explicitly generated outputs are tracked by Barabash and can be deleted on demand


.. _barabash-installation:

Installation
============

You can install Barabash either via the Python Package Index (PyPI)
or from source.

To install using `pip`,::

    $ pip install -U Barabash

To install using `easy_install`::

    $ easy_install -U Barabash

.. _getting-help:

Getting Help
============

.. _mailing-list:

Mailing list
------------

For any discussion about usage or development of Barabash, you are welcomed to join
the `Barabash mailing list`_ .

.. _`Barabash mailing list`: http://groups.google.com/group/barabash/

Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them
to BitBucket `issue tracker`_.

.. _`issue tracker`: https://bitbucket.org/godfryd/barabash/issues?status=new&status=open

License
=======
MIT

Contributors
============
Michal Nowikowski <godfryd@gmail.com>
