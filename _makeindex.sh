#!/bin/bash
set -e
echo "<html><body><ul>" > index.html
ls | egrep 'branches' | perl -e 'while(<>) { chop $_;  print "<li><a href=\"./$_\">$_</a></li>";} print "</ul>"' >> index.html
ls | egrep '(whl)' | perl -e 'while(<>) { chop $_;  print "<li><a href=\"./$_\">$_</a></li>";} print "</ul>"' >> index.html
echo "</body></html>" >> index.html
