#!/usr/bin/env python3

import os
import sys
import glob
from collections import namedtuple, defaultdict
from pathlib import Path

from jinja2 import Template
import bisect


tpl = '''
<!doctype html>
<head>
<title>pyMOR Wheels</title>
</head>
<body>
<h1>{{ tree.name }}</h1>
<pre>
to install latest:
{% if tree.name == 'master' %}
pip install --find-links=https://wheels.pymor.org/index.html pymor
{% else %}
pip install --find-links=https://wheels.pymor.org/branches/{{tree.name}}/index.html pymor
{% endif  %}
</pre>
<ul>
{%- for wheel in tree.wheels %}
    <li><a href="{{ wheel }}">
        {{ wheel }}
    </a></li>
{%- endfor %}
</ul>

{% if tree.subdirs %}
<h1>Branches</h1>
<ul>
    {%- for branch, wheels in tree.subdirs.items() -%}
    <li>
      <a href="branches/{{ branch }}/index.html">{{ branch }}</a>
    </li>
    {%- endfor %}
</ul>
{% endif %}

</body>
</html>
'''

Tree = namedtuple('Tree', 'name wheels subdirs')


def _make_tree(root, name='master'):
    files = []
    for it in root.iterdir():
        if it.is_file() and it.name.endswith('.whl'):
            files.append(it.name)
    files = sorted(files)
    branch_root = root / 'branches'
    branch_wheels = None
    if branch_root.is_dir():
        branch_wheels = defaultdict(list)
        branches = sorted([b.name for b in branch_root.iterdir() if b.is_dir()])
        for branch in branches:
            branch_dir = branch_root / branch
            for it in branch_dir.iterdir():
                if it.is_file() and it.name.endswith('.whl'):
                    bisect.insort(branch_wheels[branch], it.name)
            make_index(branch_dir, name=branch)
    return Tree(name, files, branch_wheels)


def make_index(path, name='master'):
    path = path.resolve()
    with (path / 'index.html').open('wt') as out:
        out.write(Template(tpl).render(tree=_make_tree(path, name)))


if __name__ == '__main__':
    try:
        path = Path(sys.argv[1])
    except IndexError:
        path = Path().cwd()
    make_index(path)
