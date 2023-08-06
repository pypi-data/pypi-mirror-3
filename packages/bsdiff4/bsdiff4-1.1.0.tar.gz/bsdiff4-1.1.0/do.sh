#!/bin/bash

for PY in 2.5 2.6 2.7 3.2
do
    PYBIN=$HOME/$PY/bin/python
    rm -rf $HOME/$PY/lib/python$PY/site-packages
    $PYBIN -V
    rm -rf build dist
#    $PYBIN setup.py install >/dev/null 2>&1 || exit 1
    $PYBIN setup.py install || exit 1
    pushd /tmp
    $PYBIN -c "import bsdiff4; assert bsdiff4.test(verbosity=2).wasSuccessful()" || \
        exit 1
    popd
done
