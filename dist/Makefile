PKGTITLE="munkicon"
PKGVERSION=1.0.$(shell /bin/date '+%Y%m%d')
BUNDLEID="com.github.carlashley.munkicon"
PROJECT="munkicon"
REQUIREMENTS="./dist/requirements.plist"
COMPONENT_PKG=${PKGTITLE}-${PKGVERSION}.component.pkg
DIST_PKG=munkicon-${PKGVERSION}.pkg
DIST_DIR="./dist/pkg"
# Version tracking for custom munki build.
$(shell echo ${PKGVERSION} > ./dist/version)


pkg:
	rm -f dist/pkg/munkicon-*.pkg
	pkgbuild --root ./src \
		--scripts ./scripts \
		--filter '.DS_Store' \
		--filter '__pycache__' \
		--identifier ${BUNDLEID} \
		--version ${PKGVERSION} \
		--ownership recommended \
		--preserve-xattr ${DIST_DIR}/${COMPONENT_PKG}
	productbuild --identifier ${BUNDLEID} \
		--product ${REQUIREMENTS} \
	    --package ${DIST_DIR}/${COMPONENT_PKG} ${DIST_DIR}/${DIST_PKG}
	rm -f ${DIST_DIR}/${COMPONENT_PKG}
