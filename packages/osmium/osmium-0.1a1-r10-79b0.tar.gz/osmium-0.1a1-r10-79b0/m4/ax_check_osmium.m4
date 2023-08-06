#
# SYNOPSIS
#
#   AX_CHECK_OSMIUM
#
# DESCRIPTION
#
#   Check for the osmium library. 
#
# LICENSE
#
#   Copyright 2012 Johannes Kolb <johannes.kolb@gmx.net>
#
# Based on ax_check_gd.m4 by:
#   Copyright (c) 2008 Nick Markham <markhn@rpi.edu>
#
#   Copying and distribution of this file, with or without modification, are
#   permitted in any medium without royalty provided the copyright notice
#   and this notice are preserved. This file is offered as-is, without any
#   warranty.

#serial 8

AC_DEFUN([AX_CHECK_OSMIUM], [
	AC_ARG_WITH(osmium,
		AS_HELP_STRING([--with-osmium(=DIR)], [use the osmium library (in DIR)]),,
		with_osmium=yes)

	if test "$with_osmium" != "no"; then
                OSMIUM_CPPFLAGS="-I$with_osmium"

		save_CPPFLAGS="$CPPFLAGS"
		CPPFLAGS="$OSMIUM_CPPFLAGS $CPPFLAGS"

                AC_LANG_PUSH([C++])
                AC_CHECK_HEADER([osmium/osm.hpp], [
                    AC_DEFINE(HAVE_OSMIUM, 1, [ Define if you have osmium library. ])
                    ], with_osmium=no)
                AC_LANG_POP([C++])

		CPPFLAGS="$save_CPPFLAGS"
	fi

	if test "$with_osmium" = "no"; then
		OSMIUM_CPPFLAGS="";
	fi

	AC_SUBST(OSMIUM_CPPFLAGS)
])
