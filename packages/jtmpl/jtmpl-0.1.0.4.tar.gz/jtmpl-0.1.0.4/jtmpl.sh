#!/bin/bash
APPDIR=$(dirname $(readlink $0 ) )
python ${APPDIR}/jtmpl.py $@

