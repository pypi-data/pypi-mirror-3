#!/bin/sh

find . -follow -name \*.pyc -exec rm -f \{\} \;
find . -follow -name \*.pyo -exec rm -f \{\} \;
find . -follow -name \*~ -exec rm -f \{\} \;
find . -follow -name \#* -exec rm -f \{\} \;