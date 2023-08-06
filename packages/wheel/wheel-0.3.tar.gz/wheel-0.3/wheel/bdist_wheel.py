"""Create a wheel (.whl) distribution.

A wheel is a built archive format. 
"""

import csv
import hashlib
import os
import sys
import sysconfig
import pkg_resources

from shutil import rmtree
from email.parser import Parser
from email.generator import Generator

from distutils.util import get_platform
from distutils.core import Command

from distutils import log as logger
import shutil

class bdist_wheel(Command):

    description = 'create a wheel distribution'

    user_options = [('bdist-dir=', 'd',
                     "temporary directory for creating the distribution"),
                    ('plat-name=', 'p',
                     "platform name to embed in generated filenames "
                     "(default: %s)" % get_platform()),
                    ('keep-temp', 'k',
                     "keep the pseudo-installation tree around after " +
                     "creating the distribution archive"),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in"),
                    ('skip-build', None,
                     "skip rebuilding everything (for testing/debugging)"),
                    ('relative', None,
                     "build the archive using relative paths"
                     "(default: false)"),
                    ('owner=', 'u',
                     "Owner name used when creating a tar file"
                     " [default: current user]"),
                    ('group=', 'g',
                     "Group name used when creating a tar file"
                     " [default: current group]"),
                   ]

    boolean_options = ['keep-temp', 'skip-build', 'relative']

    def initialize_options(self):
        self.bdist_dir = None
        self.data_dir = None
        self.plat_name = None
        self.format = 'zip'
        self.keep_temp = False
        self.dist_dir = None
        self.distinfo_dir = None
        self.egginfo_dir = None
        self.root_is_purelib = None
        self.skip_build = None
        self.relative = False
        self.owner = None
        self.group = None

    def finalize_options(self):
        if self.bdist_dir is None:
            bdist_base = self.get_finalized_command('bdist').bdist_base
            self.bdist_dir = os.path.join(bdist_base, 'wheel')
             
        self.data_dir = self.distribution.get_fullname() + '.data'
        
        need_options = ('dist_dir', 'plat_name', 'skip_build')
        
        self.set_undefined_options('bdist',
                                   *zip(need_options, need_options))
        
        self.root_is_purelib = self.distribution.is_pure()        

    def get_abbr_impl(self):
        """Return abbreviated implementation name"""
        if hasattr(sys, 'pypy_version_info'):
            pyimpl = 'pp'
        elif sys.platform.startswith('java'):
            pyimpl = 'jy'
        elif sys.platform == 'cli':
            pyimpl = 'ip'
        else:
            pyimpl = 'cp'
        return pyimpl

    def get_archive_basename(self):
        """Return archive name without extension"""
        purity = self.distribution.is_pure()
        impl_ver = sysconfig.get_config_var("py_version_nodot")
        plat_name = 'noarch'
        abi_tag = 'noabi'
        impl_name = 'py'
        if not purity:
            plat_name = self.plat_name.replace('-', '_').replace('.', '_')
            impl_name = self.get_abbr_impl()
            # PEP 3149 -- no SOABI in Py 2
            # For PyPy?
            # "pp%s%s" % (sys.pypy_version_info.major, 
            # sys.pypy_version_info.minor)
            abi_tag = sysconfig.get_config_vars().get('SOABI', abi_tag)
            abi_tag = abi_tag.rsplit('-', 1)[-1]
        archive_basename = "%s-%s%s-%s-%s" % (
                self.distribution.get_fullname(),
                impl_name,
                impl_ver,
                abi_tag,
                plat_name)
        return archive_basename

    def run(self):
        build_scripts = self.reinitialize_command('build_scripts')
        build_scripts.executable = 'python'

        if not self.skip_build:
            self.run_command('build')

        install = self.reinitialize_command('install',
                                            reinit_subcommands=True)
        install.root = self.bdist_dir
        install.compile = False
        install.skip_build = self.skip_build
        install.warn_dir = False

        # Use a custom scheme for the archive, because we have to decide
        # at installation time which scheme to use.
        for key in ('headers', 'scripts', 'data', 'purelib', 'platlib'):
            setattr(install,
                    'install_' + key,
                    os.path.join(self.data_dir, key))
                        
        if self.root_is_purelib:
            setattr(install,
                   'install_purelib',
                   '')
        else:
            setattr(install,
                    'install_platlib',
                    '')

        logger.info("installing to %s", self.bdist_dir)
        if False:
            self.fixup_data_files()
        self.run_command('install')

        archive_basename = self.get_archive_basename()

        pseudoinstall_root = os.path.join(self.dist_dir, archive_basename)
        if not self.relative:
            archive_root = self.bdist_dir
        else:
            archive_root = os.path.join(
                self.bdist_dir,
                self._ensure_relative(install.install_base))

        self.set_undefined_options('install_egg_info', ('target', 'egginfo_dir'))
        self.distinfo_dir = os.path.join(self.bdist_dir, 
                                         '%s.dist-info' % self.distribution.get_fullname())
        self.egg2dist(self.egginfo_dir, 
                      self.distinfo_dir)

        self.write_wheelfile(self.distinfo_dir)
        
        self.write_record(self.bdist_dir, self.distinfo_dir)            

        # Make the archive
        filename = self.make_archive(pseudoinstall_root,
                                     self.format, root_dir=archive_root)
        
        os.rename(filename, filename[:-3] + 'whl')

        if not self.keep_temp:
            if self.dry_run:
                logger.info('removing %s', self.bdist_dir)
            else:
                rmtree(self.bdist_dir)
                
    def write_wheelfile(self, wheelfile_base, packager='bdist_wheel'):
        from email.message import Message
        msg = Message()
        msg['Wheel-Version'] = '0.1' # of the spec
        msg['Packager'] = packager
        msg['Root-Is-Purelib'] = str(self.root_is_purelib).lower()
        wheelfile_path = os.path.join(wheelfile_base, 'WHEEL')
        logger.info('creating %s', wheelfile_path)
        with open(wheelfile_path, 'w') as f:
            Generator(f, maxheaderlen=0).flatten(msg)
                
    def fixup_data_files(self):
        """Put all resources in a .data directory"""
        # (only useful in the packaging/distutils2 version of bdist_wheel)
        data_files = {}
        for k, v in self.distribution.data_files.items():
            # {dist-info} is already in our directory tree
            if v.startswith('{') and not v.startswith('{dist-info}'):
                # XXX assert valid (in sysconfig.get_paths() or 'distribution.name')
                data_files[k] = os.path.join(self.data_dir,
                                             v.replace('{', '').replace('}', ''))
        self.distribution.data_files.update(data_files)

    def _ensure_relative(self, path):
        # copied from dir_util, deleted
        drive, path = os.path.splitdrive(path)
        if path[0:1] == os.sep:
            path = drive + path[1:]
        return path
    
    def _to_requires_dist(self, requirement):
        requires_dist = []        
        for op, ver in requirement.specs:
            # PEP 345 specifies but does not use == as part of a version spec
            if op == '==':
                op = ''
            requires_dist.append(op + ver)
        if not requires_dist:
            return ''
        return " (%s)" % ','.join(requires_dist)
    
    def _pkginfo_to_metadata(self, egg_info_path, pkginfo_path):
        # XXX does Requires: become Requires-Dist: ?
        # (very few source packages include Requires: (644) or 
        # Requires-Dist: (5) in PKG-INFO); packaging treats both identically
        pkg_info = Parser().parse(open(pkginfo_path))
        pkg_info.replace_header('Metadata-Version', '1.2')
        requires_path = os.path.join(egg_info_path, 'requires.txt')
        if os.path.exists(requires_path):
            requires = open(requires_path).read()
            for extra, reqs in pkg_resources.split_sections(requires):
                condition = ''
                if extra:
                    pkg_info['Provides-Extra'] = extra
                    condition = '; extra == %s' % repr(extra)
                for req in reqs:
                    parsed_requirement = pkg_resources.Requirement.parse(req)
                    spec = self._to_requires_dist(parsed_requirement)
                    pkg_info['Requires-Dist'] = parsed_requirement.key + spec + condition
        return pkg_info
    
    def egg2dist(self, egginfo_path, distinfo_path):
        """Convert an .egg-info directory into a .dist-info directory"""
        pkginfo_path = os.path.join(egginfo_path, 'PKG-INFO')
        pkg_info = self._pkginfo_to_metadata(egginfo_path, pkginfo_path)
        
        # 'safer delete'?
        if os.path.exists(distinfo_path) and not os.path.islink(distinfo_path):
            shutil.rmtree(distinfo_path)
        elif os.path.exists(distinfo_path):
            os.unlink(distinfo_path)
            
        shutil.copytree(egginfo_path, distinfo_path, 
                        ignore=lambda x, y: set(('PKG-INFO', 'requires.txt')))
            
        with open(os.path.join(distinfo_path, 'METADATA'), 'w') as metadata:
            Generator(metadata, maxheaderlen=0).flatten(pkg_info)

        shutil.rmtree(egginfo_path)
        
    def write_record(self, bdist_dir, distinfo_dir):
        from base64 import urlsafe_b64encode
        
        record_path = os.path.join(distinfo_dir, 'RECORD')
        record_relpath = os.path.relpath(record_path, bdist_dir)
        
        def walk():
            for dir, dirs, files in os.walk(bdist_dir):
                for f in files:
                    yield os.path.join(dir, f)
                    
        def skip(path):
            return (path.endswith('.pyc') \
                or path.endswith('.pyo') or path == record_relpath)
                
        writer = csv.writer(open(record_path, 'w+'))
        for path in walk():
            relpath = os.path.relpath(path, bdist_dir)
            if skip(relpath):
                md5 = ''
                hash = ''
                size = ''
            else:
                data = open(path, 'rb').read()
                md5 = hashlib.md5(data).hexdigest()
                digest = hashlib.sha256(data).digest()
                hash = 'sha256=%s' % urlsafe_b64encode(digest).decode('latin1')
                size = len(data)
            record_path = os.path.relpath(path, bdist_dir).replace(os.path.sep, '/')
            writer.writerow((record_path, md5, size, hash))
