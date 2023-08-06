#
# SYNOPSIS
#
#   AX_CHECK_GEOS
#
# DESCRIPTION
#
#   Check for the geos library.  If geos is
#   found, the output variables GEOS_CFLAGS, GEOS_LDFLAGS and GEOS_LIBS will
#   contain the compiler flags, linker flags and libraries necessary to use
#   geos; otherwise, those variables will be empty. In addition, the symbol
#   HAVE_GEOS is defined if the library is found.
#   
#   The user may use --with-geos=no or --without-geos to skip checking for the
#   library. (The default is --with-geos=yes.) If the library is installed in
#   an unusual location, --with-geos=DIR will cause the macro to look for
#   geos-config in DIR/bin or, failing that, for the headers and libraries
#   in DIR/include and DIR/lib.
#
#   Feedback welcome!
#
# LICENSE
#
#   Copyright (c) Johannes Kolb <johannes.kolb@gmx.net>
#
#   based on ax_check_gd.m4
#     Copyright (c) 2008 Nick Markham <markhn@rpi.edu>
#
#   Copying and distribution of this file, with or without modification, are
#   permitted in any medium without royalty provided the copyright notice
#   and this notice are preserved. This file is offered as-is, without any
#   warranty.


AC_DEFUN([AX_CHECK_GEOS], [
	AC_ARG_WITH(geos,
		AS_HELP_STRING([--with-geos(=DIR)], [use the geos library (in DIR)]),,
		with_geos=yes)

	if test "$with_geos" != no; then
		AC_PATH_PROG(GEOS_CONFIG, geos-config, , [$with_geos/bin:$PATH])
		if test -n "$GEOS_CONFIG"; then
			GEOS_CFLAGS=`$GEOS_CONFIG --cflags`
			GEOS_LDFLAGS=`$GEOS_CONFIG --ldflags`
			GEOS_LIBS=`$GEOS_CONFIG --libs`
                        AC_DEFINE(HAVE_GEOS, 1, [ Define if you have geos library. ])
		fi

		save_CFLAGS="$CFLAGS"
		CFLAGS="$GEOS_CFLAGS $CFLAGS"
		save_LDFLAGS="$LDFLAGS"
		LDFLAGS="$GEOS_LDFLAGS $LDFLAGS"
                
                dnl AC_CHECK_LIB(geos, ??, [AC_DEFINE(HAVE_GEOS, 1, [ Define if you have geos library ])])

		CFLAGS="$save_CFLAGS"
		LDFLAGS="$save_LDFLAGS"
	fi

	if test "$with_geos" = "no"; then
		GEOS_CFLAGS="";
		GEOS_LDFLAGS="";
		GEOS_LIBS="";
	fi

	AC_SUBST(GEOS_CFLAGS)
	AC_SUBST(GEOS_LDFLAGS)
	AC_SUBST(GEOS_LIBS)
])
