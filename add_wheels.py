#!/usr/bin/env python3
import contextlib
import shutil
import sys
import re
import os
import subprocess
from collections import defaultdict
from pathlib import Path

from makeindex import make_index

py_regex = re.compile('(?:.*\-cp)(\d\d)(?:\-.*\.whl)')
KEEP_N_WHEELS = 10


@contextlib.contextmanager
def remember_cwd(dirname):
    curdir = os.getcwd()
    try:
        os.chdir(dirname)
        yield curdir
    finally:
        os.chdir(curdir)


def _sort_wheels(filenames):
    wheels = defaultdict(list)
    for fn in filenames:
        python = '{}.{}'.format(*py_regex.match(fn).group(1))
        wheels[python] = list(sorted(list(wheels[python]) + [fn]))
    return wheels


def _target_dir(branch='master'):
    dir = os.path.abspath(os.path.dirname(__file__))
    if branch != 'master':
        dir = os.path.join(dir, 'branches', branch)
    return dir


def _current_wheels(branch):
    dir = _target_dir(branch)
    return _sort_wheels((f.path for f in os.scandir(dir) if f.path.endswith('.whl')
                         and f.is_file() and not f.is_symlink()))


def _git_add(fn):
    tdir = _target_dir()
    with remember_cwd(tdir):
        subprocess.check_call(['git', 'add', os.path.relpath(fn, tdir)])


def _git_rm(fn):
    tdir = _target_dir()
    with remember_cwd(tdir):
        subprocess.check_call(['git', 'rm', '-f', os.path.relpath(fn, tdir)])


def _update_link(source, branch):
    target_dir = _target_dir(branch)
    link_source = os.path.relpath(source, target_dir)
    link_fn = 'pymor-{}-latest-9999.9.rc0-{}'.format(branch, link_source[link_source.find('-cp')+1:])
    with remember_cwd(target_dir):
        try:
            os.unlink(link_fn)
        except FileNotFoundError:
            pass
        os.symlink(link_source, link_fn)
    _git_add(os.path.relpath(os.path.join(target_dir, link_fn), _target_dir()))


branch = sys.argv[1]
new_wheels = _sort_wheels(sys.argv[2:])
target_dir = _target_dir(branch)
os.makedirs(target_dir, exist_ok=True)
current_wheels = _current_wheels(branch)

for py in new_wheels.keys():
    new_whl_count = len(new_wheels[py])
    current_whl_count = len(current_wheels[py])
    delete_last_n = KEEP_N_WHEELS + new_whl_count - current_whl_count
    for fn in current_wheels[py][:-delete_last_n+1]:
        _git_rm(fn)
    for fn in new_wheels[py]:
        shutil.copy(fn, target_dir)
        new_fn = os.path.join(target_dir, os.path.basename(fn))
        _git_add(new_fn)

root = Path(_target_dir())
make_index(root, name=branch)
_git_add(os.path.join(root, 'index.html'))