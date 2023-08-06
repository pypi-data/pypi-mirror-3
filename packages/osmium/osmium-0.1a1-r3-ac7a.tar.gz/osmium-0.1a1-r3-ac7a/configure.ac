dnl vim:filetype=m4

AC_INIT([Osmium for Python], [0.1], [johannes.kolb@gmx.net], [pyosmium], [http://bitbucket.org/jokoala/pyosmium])
AC_PREREQ([2.59])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([libosmpbf/fileformat.proto])

dnl Check for programs
dnl ==================

AC_PROG_CXX
AC_PROG_CC

dnl Check for libraries
dnl ===================

AX_CHECK_OSMIUM
AS_IF([test "x$with_osmium" = "xno"], [OSMIUM=no], [OSMIUM=yes])
AC_SUBST(OSMIUM)

dnl AX_BOOST_BASE([], [found_boost=yes], [found_boost=no])
dnl AX_BOOST_UNIT_TEST_FRAMEWORK

PKG_CHECK_EXISTS([zlib], [ZLIB=yes], [ZLIB=no])
AC_SUBST([ZLIB])
PKG_CHECK_EXISTS([protobuf-lite], [PROTOBUF=yes], [PROTOBUF=no])
AC_SUBST([PROTOBUF])
PKG_CHECK_EXISTS([libxml-2.0], [XML2=yes], [XML2=no])
AC_SUBST([XML2])
PKG_CHECK_MODULES([OSMDEFAULT], [zlib protobuf-lite libxml-2.0], [OSMDEFAULT=yes], [OSMDEFAULT=no])
AC_SUBST([OSMDEFAULT])

AX_LIB_EXPAT
AC_SUBST([HAVE_EXPAT])

dnl AX_LIB_SHAPELIB([], [found_shapelib=yes], [found_shapelib=no])
dnl PKG_CHECK_EXISTS([sqlite3], [found_sqlite=yes], [found_sqlite=no])
dnl AX_CHECK_GD
dnl AX_LIB_GDAL
dnl AX_CHECK_GEOS
dnl AX_CHECK_SPARSEHASH



dnl JavaScript:
dnl -----------
dnl V8 Javascript
dnl AX_CHECK_ICU([4.4],[AC_DEFINE(HAVE_ICU, 1, [ Define if you have ICU library ])],[echo "not found"])
dnl

dnl Check for header files
dnl ======================

dnl AC_CHECK_HEADER


dnl Check for typedefs, structures and compiler characteristics
dnl ===========================================================

dnl Check for library functions
dnl ===========================

dnl AC_HEADER_ASSERT


dnl Output files
dnl ============
dnl AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([sysconfig.cfg])
AC_OUTPUT

AC_MSG_RESULT([
required libraries:
OSMIUM              $with_osmium
zlib                $ZLIB
expat               $HAVE_EXPAT
xml2                $XML2
protobuf            $PROTOBUF
])

dnl additional libraries:
dnl libboost            $found_boost
dnl boost unit test     $ax_cv_boost_unit_test_framework
dnl shapelib            $found_shapelib
dnl sqlite3             $found_sqlite
dnl gd                  $with_gd
dnl gdal                $found_gdal
dnl geos                $with_geos
dnl sparsehash          $with_sparsehash
