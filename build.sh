#!/bin/sh
PKG_ROOT=./dist/pkgroot/usr/local/bin
DATE=$(date +'%Y%m%d')

echo "Provide sudo password when prompted."

if [ ! -d ${PKG_ROOT} ]; then
    /bin/mkdir -p ${PKG_ROOT}
fi

if [ ! -f ./dist/pkg ]; then
    /bin/mkdir -p ./dist/pkg
fi

if [[ ! -z ${1} ]]; then
    PYTHON=${1}
else
    PYTHON=/usr/local/bin/python3
fi

# Update 'version'
/usr/bin/sed -i '' 's/'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'/'$(date +%Y%m%d)'/g' ./src/processors/__init__.py
/usr/local/bin/python3 -m zipapp src --compress --output ${PKG_ROOT}/munkicon --python="${PYTHON}"
/bin/chmod +x ${PKG_ROOT}/munkicon
sudo /usr/sbin/chown root:wheel ${PKG_ROOT}/munkicon

/usr/bin/make -f ./dist/Makefile
