#!/usr/bin/env python3

import sys
import os
import re
import subprocess

PYTHONS = ['2.7', '3.5', '3.6', '3.7-rc']

try:
    target_dir = sys.argv[1]
except IndexError:
    target_dir = os.getcwd()
target_dir = os.path.abspath(target_dir)


def _check_install(whl, python):
    arg = ['docker', 'run', '-t', '-v', '{}:/io'.format(target_dir),
           'pymor/python:{}'.format(python),
           'bash', '-c', 'pip install /io/{}'.format(whl)]
    return subprocess.check_call(arg)


def _check_wheel(whl, python):
    arg = ['docker', 'run', '-t', '-v', '{}:/io'.format(target_dir),
           'pymor/python:{}'.format(python),
           'bash', '-c', 'wheel verify /io/{}'.format(whl)]
    return subprocess.check_call(arg)


def _get_check_files():
    if os.environ.get('TRAVIS', False):
        c_range = os.environ['TRAVIS_COMMIT_RANGE']
        cmd = ['git', 'diff', '--name-only', c_range]
        potentials = subprocess.check_output(cmd, universal_newlines=True).split('\n')
    else:
        potentials = []
        for root, dirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
            for file in files:
                potentials.append(file)
    return (p for p in potentials if p.endswith('.whl'))


py_regex = re.compile('(?:.*\-cp)(\d\d)(?:\-.*\.whl)')
for whl in _get_check_files():
    whl = os.path.basename(whl)
    if '-win' in whl:
        print('Not checking Windows Wheel {}'.format(whl), file=sys.stderr)
        continue
    python = '{}.{}'.format(*py_regex.match(whl).group(1))
    if python not in PYTHONS:
        raise RuntimeError('cannot check {}, wrong python version {}'.format(whl, python))
    _check_install(whl, python)
