=================
Custom egg upload
=================

This package provides a plugin for ``zest.releaser`` that offers to upload the
released egg via SCP or HTTP PUT (WebDAV) to a custom location (instead of or
in addition to PyPI).

To use, add a section to your ``~/.pypirc`` like the following::

    [gocept.zestreleaser.customupload]
    gocept = scp://download.gocept.com:/var/www/packages
    gocept.special = http://dav.gocept.com/special

If the name of the package being released starts with one of the keys in that
section (longest match wins, case insensitive), you will be prompted whether to
upload the egg (that was created by zest.releaser by checking out the tag) to
the given server.


Uploading Documentation
=======================

In addition to uploading the egg, the plugin also offers to upload generated
documentation.

To use this functionality, create a ``~/.zestreleaserrc`` that contains
something like the following::

    [gocept.zestreleaser.customupload.doc]
    gocept = docs.gocept.com:/var/www/doc

If the name of the package being released starts with one of the keys in that
section, the plugin will run ``./bin/doc`` to generate the documentation and
then prompt to upload the contents of ``./build/doc``. The upload destination
is assembled from the configured prefix, the package name and version. In the
example, the upload location would be ``/var/www/doc/gocept.foo/1.3``.


Development
===========

The source code is available in the subversion repository at
https://code.gocept.com/svn/gocept/gocept.zestreleaser.customupload

Please report any bugs you find at
https://projects.gocept.com/projects/projects/gocept-testing/issues

