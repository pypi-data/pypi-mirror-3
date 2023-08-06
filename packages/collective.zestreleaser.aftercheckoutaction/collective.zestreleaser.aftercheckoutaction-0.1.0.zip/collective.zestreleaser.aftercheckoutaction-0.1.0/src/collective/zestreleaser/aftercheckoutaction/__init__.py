#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import os
import os.path
from subprocess import call


def split_destination(destination):
    '''Returns list of options and destination.'''

    parts = destination.split()
    options = parts[:-1]
    destination = parts[-1]
    if '://' not in destination:
        destination = 'scp://' + destination.replace(':', '/', 1)
    return (options, destination)


def action(context):
    method = choose_destination(dict(name=context['name'],
                                version=context['version']),
                                read_configuration('~/.pypirc'),
                                'collective.zestreleaser.aftercheckoutaction'
                                )
    if not method:
        return

    # Be careful, shell=True is dangerous

    call(method, shell=True)


def read_configuration(filename):
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(filename))
    return config


def choose_destination(context, config, section):
    if section not in config.sections():
        return None
    items = sorted(config.items(section, vars=context), key=lambda x: \
                   len(x[0]), reverse=True)
    package = context['name'].lower()
    for (prefix, destination) in items:
        if package.startswith(prefix.lower()):
            return destination
    return None
