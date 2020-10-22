#!/bin/sh

if [ ! -f ./dist/pkg ]; then
    /bin/mkdir -p ./dist/pkg
fi

/usr/bin/make -f ./dist/Makefile
