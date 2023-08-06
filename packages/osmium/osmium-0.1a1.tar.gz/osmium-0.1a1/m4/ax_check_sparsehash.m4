#
# SYNOPSIS
#
#   AX_CHECK_SPARSEHASH
#
# DESCRIPTION
#
#   Check for the google sparsehash library.
#   If sparsehash is
#   found, the output variable SPARSEHASH_CFLAGS will
#   contain the compiler flags. In addition, the symbol
#   HAVE_SPARSEHASH is defined if the library is found.
#
#   The user may use --with-sparsehash=no or --without-sparsehash to skip
#   checking for the library. (The default is --with-sparsehash=yes.) If the
#   library is installed in an unusual location, --with-sparsehash=DIR will
#   cause the macro to look for the headers in DIR.
#
#   Feedback welcome!
#
# LICENSE
#
#   Copyright (c) Johannes Kolb <johannes.kolb@gmx.net>
#
#   based on ax_check_gd.m4
#   Copyright (c) 2008 Nick Markham <markhn@rpi.edu>
#
#   Copying and distribution of this file, with or without modification, are
#   permitted in any medium without royalty provided the copyright notice
#   and this notice are preserved. This file is offered as-is, without any
#   warranty.

#serial 8

AC_DEFUN([AX_CHECK_SPARSEHASH], [
	AC_ARG_WITH(sparsehash,
		AS_HELP_STRING([--with-sparsehash(=DIR)], [use the google sparsehash library (in DIR)]),,
		with_sparsehash=yes)

	if test "$with_sparsehash" != no; then
		if test -d "$with_sparsehash"; then
			SPARSEHASH_CFLAGS="-I$with_sparsehash"
		fi

		save_CFLAGS="$CFLAGS"
		CFLAGS="$SPARSEHASH_CFLAGS $CFLAGS"

                AC_LANG_PUSH([C++])
                AC_CHECK_HEADER([google/sparsetable], [
                    AC_DEFINE(HAVE_SPARSEHASH, 1, [ Define if you have sparsehash library. ])
                    ], with_sparsehash=no)
                AC_LANG_POP([C++])

		CFLAGS="$save_CFLAGS"
	fi

	if test "$with_sparsehash" = "no"; then
		SPARSEHASH_CFLAGS="";
	fi

	AC_SUBST(SPARSEHASH_CFLAGS)
])
