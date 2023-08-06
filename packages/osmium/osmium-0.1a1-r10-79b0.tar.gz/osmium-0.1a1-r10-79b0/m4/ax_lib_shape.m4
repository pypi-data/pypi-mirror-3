#
AC_DEFUN([AX_LIB_SHAPELIB],
[
    AC_ARG_WITH([shapelib],
        AS_HELP_STRING([--with-shapelib=@<:@ARG@:>@],
            [use shapelib from given prefix (ARG=path)]
            ),
            [
            if test "$withval" = "yes"; then
                if test -f /usr/local/include/shapefil.h ; then
                    shapelib_prefix=/usr/local
                elif test -f /usr/include/shapefil.h ; then
                    shapelib_prefix=/usr
                fi
                shapelib_requested="yes"
            elif test -d "$withval"; then
                shapelib_prefix="$withval"
                shapelib_requested="yes"
            else
                shapelib_prefix=""
                shapelib_requested="no"
            fi
            ],
            [
            dnl Default behavior is implicit yes
            if test -f /usr/local/include/shapefil.h ; then
                shapelib_prefix=/usr/local
            elif test -f /usr/include/shapefil.h ; then
                shapelib_prefix=/usr
            else
                shapelib_prefix=""
            fi
            ]
    )

    SHAPELIB_CFLAGS=""
    SHAPELIB_LDFLAGS=""
    SHAPELIB_LIBS=""

    dnl 
    dnl Collect include/lib paths and flags
    dnl
    if test -n "$shapelib_prefix"; then
        shapelib_include_dir="$shapelib_prefix/include"
        shapelib_lib_flags="-L$shapelib_prefix/lib"
        run_shapelib_test="yes"
    else
        run_shapelib_test="no"
    fi

    dnl 
    dnl Check shapelib files
    dnl
    
    if test "$run_shapelib_test" = "yes"; then
        saved_CPPFLAGS="$CPPFLAGS"
        CPPFLAGS="$CPPFLAGS -I$shapelib_include_dir"

        saved_LDFLAGS="$LDFLAGS"
        LDFLAGS="$LDFLAGS $shapelib_lib_flags"

        AC_LANG_PUSH([C++])
        AC_CHECK_HEADER([shapefil.h], 
            [
            shapelib_header_found="yes"
            SHAPELIB_CFLAGS="-I$shapelib_include_dir"
            ],
            [
            shapelib_header_found="no"
            shapelib_found="no"
        ])
        if test "$shapelib_header_found" = "yes"; then
            AC_CHECK_LIB([shp],[SHPOpen],
                [
                shapelib_found="yes"
                SHAPELIB_LDFLAGS="$shapelib_lib_flags"
                SHAPELIB_LIBS="-lshp"
                AC_DEFINE(HAVE_SHAPEFILE, 1, [ Define if libshapefile is installed ])
                ],
                [
                shapelib_found="no"
            ])
        fi
        AC_LANG_POP([C++])

        CPPFLAGS="$saved_CPPFLAGS"
        LDFLAGS="$saved_LDFLAGS"
    else
        shapelib_found="no"
    fi

    if test "$shapelib_found" = "no"; then
        if test "$shapelib_requested" = "yes"; then
            AC_MSG_WARN([Shapelib requested but headers or library not found. Specify valid prefix using --with-shapelib=@<:@DIR@:>@.])
        fi
        ifelse([$3], , :, [$3])
    else
        ifelse([$2], , :, [$2])
    fi

    AC_SUBST([SHAPELIB_CFLAGS])
    AC_SUBST([SHAPELIB_LDFLAGS])
    AC_SUBST([SHAPELIB_LIBS])
])
