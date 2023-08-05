# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.zestreleaser.customupload',
    version='1.2',
    author='Wolfgang Schnerring <ws at gocept dot com>, Christian Zagrodnick <cz at gocept dot com>',
    author_email='ws@gocept.com',
    url='https://code.gocept.com/svn/gocept/gocept.zestreleaser.customupload',
    description="Plugin for zest.releaser to allow uploading the created egg via SCP to configurable destinations.",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    namespace_packages=['gocept', 'gocept.zestreleaser'],
    install_requires=[
        'setuptools',
        'zest.releaser>=3.12',
    ],
    extras_require=dict(test=[
        'mock',
    ]),
    entry_points={
        'zest.releaser.releaser.after':
            ['upload=gocept.zestreleaser.customupload.upload:upload',
            'upload_doc=gocept.zestreleaser.customupload.doc:upload']},
)
