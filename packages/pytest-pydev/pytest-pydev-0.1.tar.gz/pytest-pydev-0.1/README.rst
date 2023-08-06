============
pytest-pydev
============

With this plugin you can start a Python debug server on your local machine (say
on port 8042) and your unittests on another. ::

    py.test --pydevd=local-machine:8042

Obviously, in this example, instead of ``local-machine`` you use the appropriate
IP address.

A ``py.test --help`` will yield more information.


Download and Installation
=========================

You can install the plugin by running

pip install pytest-pydev

Alternatively, get the latest stable version from PyPI or the latest
bleeding-edge archive from bitbucket.org.


License and Credits
===================

This plugin is released under the MIT license. You can find the full text of the
license in the ``LICENSE`` file.

Copyright (C) 2012 Sebastian Rahlf <basti at redtoad dot de>