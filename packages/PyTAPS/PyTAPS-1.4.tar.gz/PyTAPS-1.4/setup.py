# Do this before ez_setup, since it plays with sys.path
import sys
script_dir = sys.path[0]

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Command, Extension, Feature
from setuptools import Distribution as _Distribution
from distutils.errors import DistutilsOptionError
from distutils.command.build_ext import build_ext

import re
import os

class ITAPSCommand(Command):
    @staticmethod
    def _get_defs(itaps_defs, iface):
        from parse_makefile import parse_makefile

        makefile = parse_makefile(itaps_defs)
        prefix = iface.upper()

        include_dirs = []
        library_dirs = []
        libraries = []

        inc_match = re.compile(r'(?:(?<=\s)|^)-(I)\s*(\S*)')
        for m in inc_match.finditer( makefile[prefix+'_CPPFLAGS'] ):
            if m.group(2) not in include_dirs:
                include_dirs.append( m.group(2) )

        lib_match = re.compile(r'(?:(?<=\s)|^)-([lL])\s*(\S*)')
        for m in lib_match.finditer( makefile[prefix+'_LIBS'] ):
            if m.group(1) == 'L' and m.group(2) not in library_dirs:
                library_dirs.append( m.group(2) )
            elif m.group(1) == 'l' and m.group(2) not in libraries:
                libraries.append( m.group(2) )

        return (include_dirs, library_dirs, libraries)

    @staticmethod
    def _find_defs(iface, path=None):
        if path:
            if os.path.isfile(path):
                return os.path.normpath(path)
            name = os.path.join(path, iface+'-Defs.inc')
            if os.path.isfile(name):
                return os.path.normpath(name)
            name = os.path.join(path, 'lib', iface+'-Defs.inc')
            if os.path.isfile(name):
                return os.path.normpath(name)
            raise Exception("Unable to locate %s-Defs.inc" % iface)
        elif iface.upper()+'_DEFS' in os.environ:
            name = os.getenv(iface.upper()+"_DEFS")
            if os.path.isfile(name):
                return os.path.normpath(name)
        else:
            # try a bunch of places where iXxx-Defs.inc might be located
            search = [os.path.join(i, '..', 'lib') for i in
                      os.getenv('PATH',  "").split(':') +
                      os.getenv('CPATH', "").split(':')] + \
                     os.getenv('LD_LIBRARY_PATH', "").split(':') + \
                     ['/usr/local/lib', '/usr/lib']
            for i in search:
                name = os.path.join(i, iface+'-Defs.inc')
                if os.path.isfile(name):
                    return os.path.normpath(name)

    def initialize_options(self):
        self.defs = {}

    def finalize_options(self):
        for iface in ('iMesh', 'iGeom', 'iRel'):
            if not getattr(self.distribution, "with_"+iface):
                continue

            if hasattr(self.distribution, iface+"_path"):
                path = getattr(self.distribution, iface+"_path")
                self.defs[iface] = self._get_defs(self._find_defs(iface, path),
                                                  iface)
            else:
                defs_file = self._find_defs(iface)
                if defs_file:
                    self.defs[iface] = self._get_defs(defs_file, iface)


class BuildExtCommand(build_ext, ITAPSCommand):
    def _munge_name(self, name):
        if name == 'iMeshExtensions':
            return 'iMesh'
        else:
            return name

    def _check_for_iface(self, iface, ext):
        from distutils.ccompiler import new_compiler, CompileError
        from shutil import rmtree
        import tempfile

        tmpdir = tempfile.mkdtemp()
        old = os.getcwd()

        os.chdir(tmpdir)

        # Try to include the relevant iXxx.h header, and disable the module
        # if it can't be found
        f = open('%s.c' % iface, 'w')
        f.write("#include <%s.h>\n" % iface)
        f.close()
        try:
            print "Checking for usability of %s..." % iface
            include_dirs = self.include_dirs + ext.include_dirs
            new_compiler().compile([f.name], include_dirs=include_dirs)
            success = True
        except CompileError:
            print >>sys.stderr, ("Warning: unable to find %s.h. " +
                                 "itaps.%s module disabled") % (iface, iface)
            success = False

        os.chdir(old)
        rmtree(tmpdir)
        return success

    def initialize_options(self):
        build_ext.initialize_options(self)
        ITAPSCommand.initialize_options(self)

    def finalize_options(self):
        build_ext.finalize_options(self)
        ITAPSCommand.finalize_options(self)

        # automatically include NumPy header dir if possible
        try:
            import numpy.core as nc
            self.include_dirs.append(os.path.join(nc.__path__[0], 'include'))
        except:
            pass

        # add in libs/dirs from iXxx-Defs.inc
        for m in self.extensions:
            name = self._munge_name(m.name.split(".")[1])
            if name == "iBase": # TODO: hack
                for defs in self.defs.itervalues():
                    m.include_dirs.extend(defs[0])
            elif name == "iRel": # TODO: hack
                for defs in self.defs.itervalues():
                    m.include_dirs.extend(defs[0])
                    m.library_dirs.extend(defs[1])
                    m.libraries.extend(defs[2])
            else:
                defs = self.defs.get(name)
                if defs:
                    m.include_dirs.extend(defs[0])
                    m.library_dirs.extend(defs[1])
                    m.libraries.extend(defs[2])

    def build_extension(self, ext):
        name = self._munge_name(ext.name.split('.')[1])
        if name == 'iBase' or self._check_for_iface(name, ext):
            build_ext.build_extension(self, ext)

class TestCommand(Command):
    description = 'run unit tests'
    user_options = [
        ('test-suites=','S',"Test suite to run (e.g. 'test.imesh')"),
        ]

    @staticmethod
    def meets_requirements(module):
        __import__(module)
        m = sys.modules[module]
        if not hasattr(m, '__requires__'):
            return True
        try:
            for i in m.__requires__:
                __import__(i)
            return True
        except:
            return False

    @staticmethod
    def import_recursive(module, callback=None):
        __import__(module)
        m = sys.modules[module]
        if callback: callback(m)

        if hasattr(m, '__all__'):
            for i in m.__all__:
                TestCommand.import_recursive("%s.%s" % (module, i), callback)

    def initialize_options(self):
        self.test_suites = None

    def finalize_options(self):
        if self.test_suites is None:
            # Yes, the sorting is important. For some reason it fails if we
            # test-import iRel before iMesh. This is probably a bad thing, but
            # who knows where the error lies?? (Probably iRel.)
            self.test_suites = [i for i in sorted(self.distribution.test_suites)
                                if self.meets_requirements(i)]
        else:
            self.test_suites = self.test_suites.split(",")

    def run(self):
        import unittest
        verbosity = 2 if self.verbose else 1

        runner = unittest.TextTestRunner(verbosity=verbosity)
        suite = unittest.TestSuite()
        def add_test(m):
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(m))
        for i in self.test_suites:
            self.import_recursive(i, add_test)

        res = runner.run(suite)
        if res.errors or res.failures:
            exit(1)

class DocCommand(Command):
    description = 'build documentation'
    user_options = [
        ('builder=', 'b', 'documentation builder'),
        ('target=',  't', 'target directory'),
        ]

    def initialize_options(self):
        self.builder = 'html'
        self.target = None

    def finalize_options(self):
        if self.target:
            self.target = os.path.abspath(self.target)
        else:
            self.target = '_build/' + self.builder

    def run(self):
        root = 'doc'
        old = os.getcwd()

        os.chdir(root)
        os.system('sphinx-build -b "%s" -d _build/doctrees . "%s"' %
                  (self.builder, self.target))
        os.chdir(old)        

class PerfCommand(Command):
    description = 'build/execute performance tests'
    user_options = [
        ('file=',  'F', 'file or directory containing test file(s)'),
        ('count=', 'c', 'number of times to test'),
        ]

    def initialize_options(self):
        self.file = None
        self.count = 20

    def finalize_options(self):
        if not self.file:
            raise DistutilsOptionError('"file" must be specified')

        try:
            self.count = int(self.count)
        except ValueError:
            raise DistutilsOptionError('"count" option must be an integer')

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

    sub_commands = [
        ('perf_build', None),
        ('perf_run',   None),
        ]

class PerfBuildCommand(ITAPSCommand):
    description = 'build performance tests'

    sep_by = " (separated by '%s')" % os.pathsep
    user_options = [
        ('include-dirs=', 'I',
         'list of directories to search for header files' + sep_by),
        ('libraries=', 'l',
         'external C libraries to link with'),
        ('library-dirs=', 'L',
         'directories to search for external C libraries' + sep_by),
        ]

    def initialize_options(self):
        ITAPSCommand.initialize_options(self)

    def finalize_options(self):
        ITAPSCommand.finalize_options(self)

    def run(self):
        root = 'perf'
        old = os.getcwd()
        os.chdir(root)

        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler()

        objs = self.compiler.compile(
            ['perf.c'], include_dirs=self.defs['iMesh'][0])
        self.compiler.link_executable(
            objs, 'perf', library_dirs=self.defs['iMesh'][1],
            libraries=self.defs['iMesh'][2])

        os.chdir(old)


class PerfRunCommand(Command):
    description = 'execute performance tests'
    user_options = [
        ('file=',  'F', 'file or directory containing test file(s)'),
        ('count=', 'c', 'number of times to test'),
        ]

    def initialize_options(self):
        self.file = None
        self.count = 20

    def finalize_options(self):
        self.set_undefined_options('perf',
                                   ('file', 'file'),
                                   ('count', 'count') )

        if not self.file:
            raise DistutilsOptionError('"file" must be specified')

        try:
            self.count = int(self.count)
        except ValueError:
            raise DistutilsOptionError('"count" option must be an integer')

    def run(self):
        root = 'perf'
        old = os.getcwd()
        os.chdir(root)
        os.system('python perf.py -c%d "%s"' % (self.count, self.file))
        os.chdir(old)


common_files = ['common.h', 'errors.h', 'helpers.h', 'iBase_Python.h',
                'numpy_extensions.h']

iBase = Extension(
    'itaps.iBase',
    depends = [
        'common.h', 'iBase_Python.h', 'iBase_handleTempl.def',
        'iBase_array.inl'
    ],
    sources = ['iBase.c'],
)

iMesh = Feature(
    'iMesh interface',
    standard = True,
    test_suites = ['test.imesh'],

    ext_modules = [
        Extension(
            'itaps.iMesh',
            depends = common_files + [
                'iMesh_Python.h', 'iMesh_entSet.inl', 'iMesh_iter.inl',
                'iMesh_tag.inl', 'iMesh_doc.h', 
            ],
            sources = ['iMesh.c']
        )
    ],
)

iMeshExtensions = Feature(
    'iMesh interface extensions',
    standard = True,
    require_features = ['iMesh'],
    test_suites = ['test.imeshextensions'],

    ext_modules = [
        Extension(
            'itaps.iMeshExtensions',
            depends = common_files + [
            ],
            sources = ['iMeshExtensions.c']
        )
    ],
)

iGeom = Feature(
    'iGeom interface',
    standard = True,
    test_suites = ['test.igeom'],

    ext_modules = [
        Extension(
            'itaps.iGeom',
            depends = common_files + [
                'iGeom_Python.h', 'iGeom_entSet.inl', 'iGeom_iter.inl',
                'iGeom_tag.inl', 'iGeom_doc.h',
            ],
            sources = ['iGeom.c']
        )
    ],
)

iRel = Feature(
    'iRel interface',
    standard = True,
    require_features = ['iMesh', 'iGeom'],
    test_suites = ['test.irel'],

    ext_modules = [
        Extension(
            'itaps.iRel',
            depends = common_files + [
                'iRel_Python.h', 'iRel_pair.inl', 'iRel_pairSide.inl',
                'iRel_doc.h',
                ],
            sources = ['iRel.c']
        )
   ],
)

class Distribution(_Distribution):
    global_options = _Distribution.global_options + [
        ('iMesh-path=', None, 'root directory for iMesh interface'),
        ('iGeom-path=', None, 'root directory for iGeom interface'),
        ('iRel-path=',  None, 'root directory for iRel interface'),
        ]
    test_suites = []

setup(name = 'PyTAPS',
      version = '1.4',
      description = 'Python bindings for ITAPS interfaces',
      author = 'Jim Porter',
      author_email = 'jvporter@wisc.edu',
      url = 'http://packages.python.org/PyTAPS/',

      long_description = open(os.path.join(script_dir, "README")).read(),

      classifiers = [ 'Development Status :: 5 - Production/Stable',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'Intended Audience :: Science/Research',
                      'License :: OSI Approved :: GNU Library or Lesser ' +
                          'General Public License (LGPL)',
                      'Topic :: Scientific/Engineering',
                      ],

      requires = ['numpy(>=1.3.0)'],
      setup_requires = ['numpy>=1.3.0'],
      install_requires = ['numpy>=1.3.0'],
      provides = ['itaps'],

      package_dir = {'itaps': 'pkg'},
      packages = ['itaps'],

      ext_modules = [iBase],
      py_modules = ['itaps.helpers'],
      features = { 'iMesh'           : iMesh,
                   'iMeshExtensions' : iMeshExtensions,
                   'iGeom'           : iGeom,
                   'iRel'            : iRel,
                   },
      headers = ['iBase_Python.h', 'iMesh_Python.h', 'iGeom_Python.h',
                 'iRel_Python.h', 'helpers.h'],
      scripts = ['tools/tagviewer'],

      distclass = Distribution,
      cmdclass = { 'build_ext'  : BuildExtCommand,
                   'test'       : TestCommand,
                   'doc'        : DocCommand,
                   'perf'       : PerfCommand,
                   'perf_build' : PerfBuildCommand,
                   'perf_run'   : PerfRunCommand,
                   },
      test_suites = ['test.ibase', 'test.helpers'],
      zip_safe = False,
      )
