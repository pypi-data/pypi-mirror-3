# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import ConfigParser
import glob
import os
import os.path
import urlparse
import zest.releaser.utils


def upload(context):
    destination = choose_destination(
        context['name'], read_configuration('~/.pypirc'),
        'gocept.zestreleaser.customupload')
    if not destination:
        return
    if not zest.releaser.utils.ask('Upload to %s' % destination):
        return
    sources = glob.glob(os.path.join(context['tagdir'], 'dist', '*'))
    for call in get_calls(sources, destination):
        os.system(' '.join(call))


def get_calls(sources, destination):
    result = []
    if '://' not in destination:
        destination = 'scp://' + destination.replace(':', '/', 1)
    url = urlparse.urlsplit(destination)
    if url[0] in ('scp', ''):
        netloc, path = url[1], url[2]
        assert path.startswith('/')
        path = path[1:]
        result.append(['scp'] + sources + ['%s:%s' % (netloc, path)])
    if url[0] in ('http', 'https'):
        if destination.endswith('/'):
            destination = destination[:-1]
        for source in sources:
            result.append(
                ['curl', '-X', 'PUT', '--data-binary', '@' + source,
                 '%s/%s' % (destination, os.path.basename(source))])
    return result


def read_configuration(filename):
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(filename))
    return config


def choose_destination(package, config, section):
    if section not in config.sections():
        return None
    items = sorted(config.items(section), key=lambda x: len(x[0]),
                   reverse=True)
    package = package.lower()
    for prefix, destination in items:
        if package.startswith(prefix.lower()):
            return destination
    return None
