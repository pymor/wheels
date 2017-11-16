#!/usr/bin/env python3

import os
import sys
import glob
from collections import namedtuple, defaultdict
from jinja2 import Template


tpl = '''
<!doctype html>
<head>
<title>Path: {{ tree.name }}</title>
</head>
<body>
<h1>Master</h1>
<ul>
    {%- for wheel in tree.wheels -%}
        <li><a href="{{ wheel }}">{{ wheel }}</a></li>
    {%- endfor %}
</ul>
<h1>Branches</h1>
<ul>
    {%- for branch, wheels in tree.subdirs.items() -%}
    <li><h2>{{ branch }}</h2>
        <ul>
            {%- for wheel in wheels -%}
                <li><a href="branches/{{ branch }}/{{ wheel }}">{{ wheel }}</a></li>
            {%- endfor %}
        </ul>
    </li>
    {%- endfor %}
</ul>

</body>
</html>
'''

Tree = namedtuple('Tree', 'name wheels subdirs')


def make_tree(root):
    files = []
    for it in os.scandir(root):
        if it.is_file() and it.name.endswith('.whl'):
            files.append(it.name)
    branch_root = os.path.join(root, 'branches')
    branch_wheels = defaultdict(list)
    branches = [b.name for b in os.scandir(branch_root) if b.is_dir()]
    for branch in branches:
        branch_dir = os.path.join(branch_root, branch)
        for it in os.scandir(branch_dir):
            if it.is_file() and it.name.endswith('.whl'):
                branch_wheels[branch].append(it.name)
    return Tree('branches', files, branch_wheels)

try:
    path = sys.argv[1]
except IndexError:
    path = os.getcwd()
path = os.path.abspath(path)
with open(os.path.join(path, 'index.html'), 'wt') as out:
    out.write(Template(tpl).render(tree=make_tree(path)))
