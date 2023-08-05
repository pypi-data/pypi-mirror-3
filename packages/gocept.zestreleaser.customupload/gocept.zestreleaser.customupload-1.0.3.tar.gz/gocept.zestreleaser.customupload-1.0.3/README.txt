===================
 Custom egg upload
===================

This package provides a plugin for ``zest.releaser`` that offers to upload the
released egg via SCP to a custom location (instead of / in addition to PyPI).

To use, add a section to your ``~/.pypirc`` like so::

    [gocept.zestreleaser.customupload]
    gocept = download.gocept.com:/var/www/packages
    gocept.special = download.gocept.com:/var/www/special-packages

If the package being released starts with one of the keys in that section
(longest match wins, case insensitive), you will be prompted whether to upload
the egg (that was created by zest.releaser by checking out the tag) to the
given server.
