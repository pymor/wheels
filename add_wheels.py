#!/usr/bin/env python3
import bisect
import shutil
import sys
import re
import os
from collections import defaultdict

py_regex = re.compile('(?:.*\-cp)(\d\d)(?:\-.*\.whl)')
KEEP_N_WHEELS = 2


def _sort_wheels(filenames):
    wheels = defaultdict(list)
    for fn in filenames:
        python = '{}.{}'.format(*py_regex.match(fn).group(1))
        bisect.insort(wheels[python], fn)
    return wheels


def _target_dir(branch):
    dir = os.path.abspath(os.path.dirname(__file__))
    if branch != 'master':
        dir = os.path.join(dir, 'branches', branch)
    return dir


def _current_wheels(branch):
    dir = _target_dir(branch)
    return _sort_wheels((f.path for f in os.scandir(dir) if f.path.endswith('.whl')
                         and f.is_file() and not f.is_symlink()))


def _update_link(source, branch):
    curdir = os.getcwd()
    target_dir = _target_dir(branch)
    os.chdir(target_dir)
    link_source = os.path.relpath(source, target_dir)
    link_fn = 'pymor-{}-latest-{}'.format(branch, link_source[-link_source.find('-cp'):])
    try:
        os.unlink(link_fn)
    except FileNotFoundError:
        pass
    print('{} -> {}'.format(link_source, link_fn))
    os.symlink(link_source, link_fn)
    os.chdir(curdir)


branch = sys.argv[1]
new_wheels = _sort_wheels(sys.argv[2:])
target_dir = _target_dir(branch)
os.makedirs(target_dir, exist_ok=True)
current_wheels = _current_wheels(branch)

for py in new_wheels.keys():
    new_whl_count = len(new_wheels[py])
    current_whl_count = len(current_wheels[py])
    delete_last_n = KEEP_N_WHEELS + new_whl_count - current_whl_count
    for fn in current_wheels[py][-delete_last_n:]:
        os.unlink(fn)
    for fn in new_wheels[py]:
        shutil.copy(fn, target_dir)
current_wheels = _current_wheels(branch)
for py in current_wheels.keys():
    _update_link(current_wheels[py][0], branch)