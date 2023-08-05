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

If the package being released starts with one of the keys in that section
(longest match wins, case insensitive), you will be prompted whether to upload
the egg (that was created by zest.releaser by checking out the tag) to the
given server.

