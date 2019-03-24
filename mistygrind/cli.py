#!/bin/env python
"""Command-line interface (CLI)


SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import glob
import json
import os.path
import sys
import tempfile
import uuid
import zipfile

from .__init__ import __version__


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(description='a tool for static analysis of Misty skills and offboard Misty REST API clients')
    argparser.add_argument('FILE', nargs='*', default=None,
                           help='zip files or skill meta files')
    argparser.add_argument('-V', '--version', dest='print_version',
                           action='store_true', default=False,
                           help='print version number and exit.')
    args = argparser.parse_args(argv)
    if args.print_version:
        print(__version__)
        return 0

    if not args.FILE:
        files = glob.glob('*.zip')
        files += glob.glob('*.ZIP')
    else:
        files = args.FILE

    for name in files:
        original_dirname = os.path.dirname(name)
        skillname = os.path.basename(name)
        if skillname.endswith('.json') or skillname.endswith('.JSON'):
            skillname = skillname[:-len('.json')]
        elif skillname.endswith('.zip') or skillname.endswith('.ZIP'):
            skillname = skillname[:-len('.zip')]
        else:
            print('ERROR: failed to extract skill name from {}'.format(name))
            return 1
        print('skill: {}'.format(skillname))

        temporary_path = None
        try:
            fp = zipfile.ZipFile(name, mode='r')
            temporary_path = tempfile.mkdtemp()
            fp.extractall(path=temporary_path)
            fp.close()
        except zipfile.BadZipFile:
            # not a ZIP file? try to treat as meta file
            pass

        if temporary_path:
            parentpath = temporary_path
        else:
            parentpath = original_dirname

        metafilepath = os.path.join(parentpath, '{}.json'.format(skillname))
        if not os.path.exists(metafilepath):
            metafilepath = os.path.join(parentpath, '{}.JSON'.format(skillname))
            if not os.path.exists(metafilepath):
                print('ERROR: no meta file found')
                return 1

        with open(metafilepath, 'rt') as fp:
            skillmeta = json.load(fp)

        print('comparing `Name` field in meta file with file names...')
        assert 'Name' in skillmeta, 'meta file is missing name field'
        assert skillmeta['Name'] == skillname, 'unexpected name in meta file'

        print('checking that GUID is well-formed...')
        assert 'UniqueId' in skillmeta, 'meta file is missing GUID field'
        try:
            uuid.UUID(skillmeta['UniqueId'])
        except ValueError:
            print('ERROR: not well-formed GUID: {}'.format(skillmeta['UniqueId']))
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
