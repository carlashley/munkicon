#!/bin/zsh
PKG_ROOT=./dist/pkgroot/usr/local/
DATE=$(date +'%Y%m%d')
PYTHON=/usr/local/bin/python3
PKGTITLE="munkicon"
PKGVERSION=1.0.${DATE}
BUNDLEID="com.github.carlashley.munkicon"
PROJECT="munkicon"
REQUIREMENTS="./dist/requirements.plist"
COMPONENT_PKG=${PKGTITLE}-${PKGVERSION}.component.pkg
DIST_PKG=munkicon-${PKGVERSION}.pkg
DIST_DIR="./dist/pkg"

# Usage
while getopts "c:p:h" option; do
    case $option in
        "c")
            INSTALLER_CERT="$OPTARG"
            ;;
        "p")
            PYTHON="$OPTARG"
            ;;
        "h")
            echo "Usage: ./build.sh [-c cert] [-p python]"
            echo ""
            echo "    -c cert      Specify the certificate to use to sign the package."
            echo "                 For example: \"Developer ID Installer: munkicon (U01A32EXMP)\""
            echo "    -p python    Path to the python interpreter."
            echo "                 For example: /usr/local/munki/munki-python"
            exit
            ;;
        *)
            INSTALLER_CERT=""
            ;;
    esac
done

# sudo prompt
echo "Provide sudo password when prompted."

# Ensure munkicon kick script exists and other directory structures
if [ ! -d ${PKG_ROOT} ]; then
    /bin/mkdir -p ${PKG_ROOT}/munki/conditions
    /bin/mkdir -p ${PKG_ROOT}/bin
    echo "#!/bin/zsh\n\n/usr/local/bin/munkicon" > ${PKG_ROOT}/munki/conditions/munkicon.sh
fi

# Make package dest folder if non existent
if [ ! -f ./dist/pkg ]; then
    /bin/mkdir -p ./dist/pkg
fi

# Update 'version'
/usr/bin/sed -i '' 's/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]/'$(date +%Y%m%d)'/g' ./src/processors/__init__.py

# Build the zipapp
/usr/local/bin/python3 -m zipapp src --compress --output ${PKG_ROOT}/bin/munkicon --python="${PYTHON}"

# Ensure permissions are correct
/bin/chmod +x ${PKG_ROOT}/bin/munkicon
/bin/chmod +x ${PKG_ROOT}/munki/conditions/munkicon.sh
sudo /usr/sbin/chown root:wheel ${PKG_ROOT}/bin/munkicon
sudo /usr/sbin/chown root:wheel ${PKG_ROOT}/munki/conditions/munkicon.sh

# Version tracking for builds
echo ${PKGVERSION} > ./dist/version

# Purge old packages
setopt +o nomatch
/bin/rm -f dist/pkg/munkicon-*.pkg
unsetopt +o nomatch

# Create component package
/usr/bin/pkgbuild --root ./dist/pkgroot \
	--scripts ./scripts \
	--filter '.DS_Store' \
	--filter '__pycache__' \
	--identifier ${BUNDLEID} \
	--version ${PKGVERSION} \
	--ownership recommended \
	--preserve-xattr ${DIST_DIR}/${COMPONENT_PKG}

# Create package and sign/don't sign
if [ "$INSTALLER_CERT" != "" ]; then
    if [ ! $(sw_vers -productVersion) = 12.0.1 ]; then
        /usr/bin/productbuild --identifier ${BUNDLEID} \
            --sign ${INSTALLER_CERT} \
            --package ${DIST_DIR}/${COMPONENT_PKG} ${DIST_DIR}/${DIST_PKG}
    else
        /usr/bin/productbuild --identifier ${BUNDLEID} \
            --product ${REQUIREMENTS} \
            --sign ${INSTALLER_CERT} \
            --package ${DIST_DIR}/${COMPONENT_PKG} ${DIST_DIR}/${DIST_PKG}
    fi
else
    if [ ! $(sw_vers -productVersion) = 12.0.1 ]; then
        /usr/bin/productbuild --identifier ${BUNDLEID} \
            --product ${REQUIREMENTS} \
            --package ${DIST_DIR}/${COMPONENT_PKG} ${DIST_DIR}/${DIST_PKG}
    else
        /usr/bin/productbuild --identifier ${BUNDLEID} \
            --package ${DIST_DIR}/${COMPONENT_PKG} ${DIST_DIR}/${DIST_PKG}
    fi
fi

# Delete component package
if [ ! -f ${DIST_DIR}/${DIST_PKG} ]; then
    echo 'Package build failed...'
fi

echo 'Removing temporary component package' ${DIST_DIR}/${COMPONENT_PKG}
/bin/rm -f ${DIST_DIR}/${COMPONENT_PKG}
