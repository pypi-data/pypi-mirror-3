import sys
import shlex
import os

from version import get_hg_version

# let setuptools believe, Pyrex is there
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fake_pyrex"))

# Try importing setuptools, use distutils otherwise
try:
    import pkg_resources
    try:
        pkg_resources.require('setuptools')
    except pkg_resources.ResolutionError:
        raise ImportError

    from setuptools import setup
    from setuptools.extension import Extension


except ImportError:
    print("no setuptools installed, using distutils")
    from distutils.core import setup
    from distutils.extension import Extension


from distutils.command.build import build as Distutils_Build
from distutils.command.config import config as Distutils_Config
from distutils.errors import DistutilsExecError, DistutilsModuleError
from distutils.spawn import find_executable

try:
    from configparser import ConfigParser, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError

from pprint import pprint

def fake_cythonize(ext_modules):
    """replacement for cythonize, if no cython installed

    Replaces .pyx with .cpp and checks, if files available
    """
    for ext in ext_modules:
        new_sources=[]
        for src in ext.sources:
            if os.path.splitext(src)[1] == '.pyx':
                cppfile = os.path.splitext(src)[0]+'.cpp'
                if not os.path.isfile(cppfile):
                    print("Cythonized file "+cppfile+" missing.")
                    raise DistutilsModuleError("need Cython to build development version")
                new_sources.append(cppfile)
            else:
                new_sources.append(src)
        ext.sources=new_sources
    raise DistutilsModuleError("failed dependencies")

# Try importing Cython, use fake_cythonize otherwise
try:
    import pkg_resources
    try:
        pkg_resources.require('Cython>=0.15.1')
        from Cython.Build import cythonize
    except pkg_resources.ResolutionError:
        raise ImportError

except ImportError:
    print("no Cython installed, using fake_cython")
    cythonize = fake_cythonize

class AutoConfig(Distutils_Config):
    """Spawn autoconfig and read results
    """

    user_options = [
            ('autoconf=', None,
                "specify autoconf parameters"),
            ('force', 'f',
                "forcibly build everything (ignore file timestamps)"),
            ]

    def initialize_options(self):
        self.autoconf = ''
        self.force = False

    def finalize_options(self):
        pass

    def run(self):
        # if autotools installed, update configure script
        if find_executable('autoreconf'):
            self.make_file('configure.ac', 'configure', lambda: self.spawn(['autoreconf']), [])
        elif not os.path.isfile('configure'):
            raise DistutilsModuleError("need GNU autotools to build development version")


        # run configure, using previous parameters if available
        if not os.path.isfile('config.status'):
            self.spawn(['configure']+shlex.split(self.autoconf), search_path=0)
        elif self.force:
            os.chmod('config.status', 0o755)
            self.spawn(['config.status','--recheck'], search_path=0)
            self.spawn(['config.status'], search_path=0)

        # parse generated config file
        autoconfig = ConfigParser()
        if not autoconfig.read('sysconfig.cfg'):
            raise DistutilsModuleError("sysconfig.cfg is missing")

        
        # search for missing libraries
        missing = []

        for lib in ('osmium', 'expat', 'zlib', 'protobuf', 'xml2'):
            if autoconfig.get('libs',lib) != 'yes':
                missing += [lib]

        if missing:
            print("The following libraries are missing:\n"+str(missing))
            os.unlink('config.status')
            raise DistutilsModuleError("failed dependencies")
        
        self.distribution.autoconfig = autoconfig


class MyBuild(Distutils_Build):

    def run(self):
        # make sure, everything is configured
        self.run_command("config")

        # build libosmpbf
        self.spawn(["make", "-C", "libosmpbf"])

        # cythonize program
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules)

        # add compiler flags and libraries from configure step
        self.add_compile_options(self.distribution.ext_modules)

        # and do the build
        Distutils_Build.run(self)

    def add_compile_options(self, ext_modules):
        """adds compiler and linker options from configure script

        Iterates through all libraries of `ext_modules` and replaces all known libraries
        by their compile and linker flags.

        Example entry in sysconfig.cfg for the "foo" library:
        foo = yes
        foo_cflags = -I/usr/include/foo
        foo_libs  = -L/usr/lib/foo -lfoo
        """
        autoconfig = self.distribution.autoconfig

        for ext in ext_modules:
            new_libs = []
            for lib in ext.libraries:
                if autoconfig.has_option('libs', lib):
                    if autoconfig.get('libs',lib) == 'no':
                        raise DistutilsModuleError("can't build "+ext.name+": dependency "+lib+" is missing")

                    try:
                        ext.extra_compile_args.extend(shlex.split(autoconfig.get('libs',lib+'_cflags')))
                    except NoOptionError:
                        pass
                    try:
                        ext.extra_link_args.extend(shlex.split(autoconfig.get('libs', lib+'_libs')))
                    except NoOptionError:
                        pass
                else:
                    new_libs.append(lib)
            ext.libraries = new_libs
            #pprint(ext.__dict__)


#################################
# real configuration starts here

default_parms = {
        "language": "c++",
        "define_macros": [('OSMIUM_WITH_OUTPUT_OSM_XML', 1)],
        }

ext_modules = [
        Extension("osmium.core", ["osmium/core.pyx"],
            libraries=['osmium', 'osmdefault', 'expat', 'osmpbf'],
            **default_parms
            ),
        Extension("osmium.osm", ["osmium/osm.pyx"],
            libraries=['osmium'],
            **default_parms
            ),
        Extension("osmium.handler", ["osmium/handler.pyx"],
            libraries=['osmium', 'osmdefault', 'expat', 'osmpbf'],
            **default_parms
            ),
        Extension("osmium.examples", ["osmium/examples.pyx"],
            libraries=['osmium', 'osmdefault', 'expat', 'osmpbf'],
            **default_parms
            ),
        Extension("osmium.output", ["osmium/output.pyx"],
            libraries=['osmium', 'osmdefault', 'expat', 'osmpbf'],
            **default_parms
            ),
        ]

descfile=open('README.txt')
long_description = descfile.read()
descfile.close()

classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: C++",
        ]

setup(
        name="osmium",
        version=get_hg_version(),
        author='Johannes Kolb',
        author_email='johannes.kolb@gmx.net',
        maintainer='Johannes Kolb',
        maintainer_email='johannes.kolb@gmx.net',
        url='http://www.bitbucket.org/jokoala/pyosmium',
        description='Osmium OSM processing library for Python',
        long_description=long_description,
        keywords=["OSM", "Open Street Map", "Osmium"],
        classifiers = classifiers,
        license='GPL',
        packages=['osmium'],
        cmdclass={'config': AutoConfig, 'build': MyBuild},
        ext_modules=ext_modules,
        )
