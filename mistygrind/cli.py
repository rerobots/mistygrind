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
import subprocess
import sys
import tempfile
import uuid
import zipfile

from .__init__ import __version__
from .vm import start_vm


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(description='a tool for static analysis of Misty skills and offboard Misty REST API clients')
    argparser.add_argument('FILE', nargs='*', default=None,
                           help='zip files or skill meta files')
    argparser.add_argument('-V', '--version', dest='print_version',
                           action='store_true', default=False,
                           help='print version number and exit.')
    argparser.add_argument('--check-deps', dest='check_dependencies',
                           action='store_true', default=False,
                           help='check for dependencies, like ESLint.')
    argparser.add_argument('--vm', dest='run_vm',
                           action='store_true', default=False,
                           help='start Misty mock REST API server')
    args = argparser.parse_args(argv)
    if args.print_version:
        print(__version__)
        return 0

    if args.run_vm:
        return start_vm()

    if args.check_dependencies:
        args = ['eslint', '--version']
        try:
            rc = subprocess.call(args, stdout=subprocess.PIPE)
        except OSError:
            print('ESLint not found. Try to install it as instructed at\n'
                  'https://eslint.org/docs/user-guide/getting-started')
            print('It might suffice to use Yarn (https://yarnpkg.com/en/):\n\n'
                  '    yarn global add eslint\n')
            return 1
        if rc != 0:
            print('ESLint does not appear to be correctly installed. '
                  'Compare with instructions at\n'
                  'https://eslint.org/docs/user-guide/getting-started')
            return 1
        return 0

    if not args.FILE:
        files = glob.glob('*.zip')
        files += glob.glob('*.ZIP')
    else:
        files = args.FILE

    for ii, name in enumerate(files):
        if ii > 0:
            print('----')
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

        jsfilepath = os.path.join(parentpath, '{}.js'.format(skillname))
        if not os.path.exists(jsfilepath):
            jsfilepath = os.path.join(parentpath, '{}.JS'.format(skillname))
            if not os.path.exists(jsfilepath):
                print('ERROR: no JS file found')
                return 1

        with open(metafilepath, 'rt') as fp:
            try:
                skillmeta = json.load(fp)
            except ValueError:
                print('ERROR: meta file does not contain valid JSON')
                return 1

        print('comparing `Name` field in meta file with file names...')
        if 'Name' not in skillmeta:
            print('ERROR: meta file is missing name field')
            return 1
        if skillmeta['Name'] != skillname:
            print('ERROR: unexpected name in meta file')
            return 1

        print('checking that GUID is well-formed...')
        if 'UniqueId' not in skillmeta:
            print('ERROR: meta file is missing GUID field')
            return 1
        try:
            uuid.UUID(skillmeta['UniqueId'])
        except ValueError:
            print('ERROR: not well-formed GUID: {}'.format(skillmeta['UniqueId']))
            return 1

        print('checking syntax of main JS file...')
        eslint_rulespath = os.path.join(os.path.dirname(__file__), 'eslint_rules')
        args = ['eslint',
                '--no-eslintrc',
                '--rulesdir', eslint_rulespath,
                '--rule', 'mistyobj-prop: 2',
                jsfilepath]
        subprocess.check_call(args)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
