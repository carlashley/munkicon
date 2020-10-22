PKGTITLE="munkicon"
PKGVERSION=1.0.$(shell /bin/date '+%Y%m%d')
BUNDLEID="com.github.carlashley.munkicon"
PROJECT="munkicon"


pkg:
	rm -f dist/pkg/munkicon-*.pkg
	pkgbuild --root ./src \
		--scripts ./scripts \
		--filter '.DS_Store' \
		--filter '__pycache__' \
		--identifier ${BUNDLEID} \
		--version ${PKGVERSION} \
		--ownership recommended \
		--preserve-xattr ./dist/pkg/${PKGTITLE}-${PKGVERSION}.component.pkg
	productbuild --identifier ${BUNDLEID} --package ./dist/pkg/${PKGTITLE}-${PKGVERSION}.component.pkg ./dist/pkg/munkicon-${PKGVERSION}.pkg
	rm -f dist/pkg/${PKGTITLE}-${PKGVERSION}.component.pkg
