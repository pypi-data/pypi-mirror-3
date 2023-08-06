#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    * Orbit :: Virtual environment management for Meteor.js

    * Copyright: (c) 2012 by Jesse Bounds
    * License: MIT, see LICENSE for more details.

    Usage:
      orbit.py contain --meteor_version <version> <environment_directory>
      orbit.py -h | --help
      orbit.py --version

    Options:
      -h --help     Show this screen.
      --version     Show version.
"""

import os
import logging
import urllib2
import tarfile
from docopt import docopt

ACTIVATE_SH = """
    # This file must be used with "source bin/activate" *from bash*
    # you cannot run it directly
    PATH="__VIRTUAL_ENV__/meteor/bin:$PATH"
    export PATH

    PS1="__VIRTUAL_PROMPT__$PS1"
    export PS1
"""

orbit_version = '0.0.1'
logger = None
join = os.path.join
abspath = os.path.abspath


def create_logger():
    """
    Create logger
    """
    # create logger
    logger = logging.getLogger("orbit")
    logger.setLevel(logging.INFO)

    # monkey patch
    def emit(self, record):
        msg = self.format(record)
        fs = "%s" if getattr(record, "continued", False) else "%s\n"
        self.stream.write(fs % msg)
        self.flush()
    logging.StreamHandler.emit = emit

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter(fmt="%(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


def mkdir(path):
    """
    Create directory
    """
    if not os.path.exists(path):
        logger.info(' * Creating: %s ... ', path, extra=dict(continued=True))
        os.makedirs(path)
        logger.info('done.')
    else:
        logger.info(' * Directory %s already exists', path)


def writefile(dest, content, overwrite=True):
    """
    Create file and write content in it
    """
    if not os.path.exists(dest):
        logger.info(' * Writing %s ... ', dest, extra=dict(continued=True))
        f = open(dest, 'wb')
        f.write(content.encode('utf-8'))
        f.close()
        logger.info('done.')
        return
    else:
        f = open(dest, 'rb')
        c = f.read()
        f.close()
        if c != content:
            if not overwrite:
                logger.info(' * File %s exists with different content; \
                    not overwriting', dest)
                return
            logger.info(' * Overwriting %s with new content', dest)
            f = open(dest, 'wb')
            f.write(content.encode('utf-8'))
            f.close()
        else:
            logger.info(' * Content %s already in place', dest)


def install_activate(env_dir, bin_directory):
    """
    Install virtual environment activation script
    """
    files = {'activate': ACTIVATE_SH}
    prompt = '(%s)' % os.path.basename(os.path.abspath(env_dir))

    for name, content in files.items():
        file_path = join(bin_directory, name)
        content = content.replace('__VIRTUAL_PROMPT__', prompt)
        content = content.replace('__VIRTUAL_ENV__', os.path.abspath(env_dir))
        writefile(file_path, content)
        os.chmod(file_path, 0755)


def main():
    arguments = docopt(__doc__, version='Orbit %s' % orbit_version)
    global logger
    logger = create_logger()

    user_directory = arguments['<environment_directory>']
    bin_directory = "%s/bin" % user_directory

    # create user's desired working directory
    mkdir(user_directory)
    mkdir(bin_directory)
    install_activate(user_directory, bin_directory)

    meteor_package_url = \
        'https://d3sqy0vbqsdhku.cloudfront.net/' \
        'meteor-package-%s-x86_64-%s.tar.gz' \
        % (os.uname()[0], arguments['<version>'])
    logger.info(" * Downloading %s ... ", meteor_package_url, \
        extra=dict(continued=True))
    u = urllib2.urlopen(meteor_package_url)
    file_name = '%s/meteor-package-%s-x86_64-%s.tar.gz' % \
        (user_directory, os.uname()[0], arguments['<version>'])
    localFile = open(file_name, 'w')
    localFile.write(u.read())
    localFile.close()
    logger.info("done.")

    logger.info(" * Extracting meteor tarfile to %s ... ", \
        file_name, extra=dict(continued=True))
    logger.info("done.")
    tar = tarfile.open(file_name)
    tar.extractall(user_directory)
    tar.close()


if __name__ == '__main__':
    main()
