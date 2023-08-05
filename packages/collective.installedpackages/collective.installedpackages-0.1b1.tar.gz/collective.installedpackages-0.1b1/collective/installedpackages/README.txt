Introduction
============

Add-on for Plone to list all Python packages available to the running Python process, its versions
and other information about them.

This add-on depends heavily on yolk_.

Once installed the add-on makes available two views:

- ``@@list-python-packages``: list all Python packages available to the running Python process, its
  versions and other information about them.
  
- ``@@list-sys-path``: show the value of ``sys.path``.

It also installs a configlet in the Plone control-panel that allows access to these two views.

Only manager users can access the views and the configlet.

.. References:
.. _yolk: http://pypi.python.org/pypi/yolk

