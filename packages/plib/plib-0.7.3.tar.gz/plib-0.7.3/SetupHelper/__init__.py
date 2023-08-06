#!/usr/bin/env python
"""
SetupHelper -- helper module to automate setup boilerplate
Copyright (C) 2008-2009 by Peter A. Donis

Released under the Python Software Foundation License.

This setup helper module automates much of the boilerplate.
The entry point is the setup_main function, which expects to be
called with a dictionary mapping variable names to values; the
supported variable names are listed below.

The recommended way to call setup_main is to first define all the
necessary variables as module globals in your setup.py file, and
then simply do:

    from SetupHelper import setup_main
    setup_main(globals())

This will pass your module globals to SetupHelper, which will then
do all the grunt work! (SetupHelper automatically filters out globals
like __name__, __file__, and so on that are supplied by Python, so they
won't interfere with yours.)

The variable names supported are as follows (most of them map in a
fairly obvious way to setup keyword arguments):

__progname__           -- name of the program
__version__            -- program version (TODO: add __dev_build__)
__dev_status__         -- string indicating the development status;
                          this is a shortcut way of adding the
                          corresponding Trove classifier, so if you
                          use it you don't need to include the
                          classifier in __classifiers__; this
                          variable is here because it is also
                          useful in determining archive names
__description__        -- one-line description

__long_description__   -- triple-quoted string containing long
                          description (may be read from README
                          instead, if so use next two variables
                          and omit this one)
__start_line__         -- contents of the line in README where the
                          long description should start (i.e.,
                          this line and all after it until the
                          end line will be included), or the line
                          number where it should start
__end_line__           -- contents of the line in README where the
                          long description should end (i.e., this
                          line and all after it will *not* be
                          included), or the line number where it
                          should end (negative numbers count from
                          the end of the file)

__author__             -- author name
__author_email__       -- author e-mail address
__url__                -- home URL for the author or program

__download_url__       -- URL for downloading the program; should
                          not be needed, use __url_base__ and
                          __url_type__ or __url_ext__ instead
__url_base__           -- base URL for download; assumes that the
                          full download URL is of the form
                          <base>/<progname>-<version>.<ext>; if
                          omitted, the PyPI base URL will be used
__url_ext__            -- extension for the download file; can be
                          ('tar.gz', 'zip', 'exe', 'dmg'); defaults
                          to 'tar.gz' if this and the next variable
                          are both omitted
__url_type__           -- type of file being downloaded; can be
                          a valid __url_ext__ value or a valid
                          value for os.name ('posix' and 'nt'
                          are currently supported); if omitted,
                          __url_ext__ (or its default) is used

__license__            -- the name of the distribution license (valid
                          values are listed in PEP 241)
__classifiers__        -- triple-quoted string containing Trove
                          classifiers, one per line (blank lines
                          at the start and end are ignored)

__install_requires__   -- list of names of packages that this one
                          depends on; SetupHelper will attempt to
                          download each one from PyPI and install it
                          if it's not already installed (note that
                          the support for this if setuptools is not
                          used is *very* basic)
__provides__           -- list of package names that this one provides
                          (if omitted, defaults to __progname__); this
                          variable doesn't actually do anything unless
                          setuptools is being used
__obsoletes__          -- list of package names that should be removed
                          when this one is installed; again, this
                          doesn't do anything unless setuptools is used

__rootfiles__          -- list of files from the project root (the
                          setup.py directory) that should be included
                          in MANIFEST.in (optional; if not included
                          no files from the project root other than
                          the standard ones, setup.py and README,
                          and this module, SetupHelper.py, if present,
                          will be included in distributions); note that
                          this and the next variable are for files that
                          should *not* be installed but need to be in
                          the source distribution--this means that these
                          files will *not* be included in the list of
                          automatically detected Python modules (see
                          below), even if they are .py files
__rootdirs__           -- list of subdirectories of the project root
                          that should be included in MANIFEST.in; if
                          not included, only the SetupHelper directory,
                          if present, will be included (this is for
                          projects that are using the svn:externals
                          version of this helper module); note
                          that these subdirectories will *not* be
                          included in the list of automatically
                          detected packages (see below), even if they
                          include __init__.py files

__py_modules__         -- list of pure Python modules not contained
                          in packages; if omitted, it is assumed that
                          any .py files in the source 'root' (this is
                          normally the setup directory, but may be
                          changed by __package_root__ or __package_dir__,
                          see below) other than those listed in
                          __non_modules__ are pure Python modules to
                          be installed (except setup.py, which is never
                          installed)
__non_modules__        -- list of .py files in the source 'root' that
                          should not be treated as modules if modules
                          are automatically detected; note that these
                          will *not* be included in source distributions
                          either (to do that, list them in __rootfiles__)

__packages__           -- list of package names to be included; this
                          should generally not be used, using the
                          __package_root__ variable is preferred
__package_dir__        -- mapping of package names to subdirectories
                          of the setup directory; if the empty string ''
                          is a key in this mapping, it defines the
                          'root' of the source tree, equivalent to
                          setting __package_root__ (see below); this
                          should generally not be used unless you are
                          explicitly setting __packages__, which should
                          be rare; in most cases, the combination
                          of setting __package_root__ and automatic
                          detection of package subdirectories should
                          be sufficient (and since this variable does not
                          disable the functionality of the ones below,
                          interactions between them can be difficult)
__package_root__       -- subdir of the setup.py directory which is
                          the 'root' of the source tree (i.e., the
                          directory in which modules that are not in
                          any package live); this will be used as the
                          root of the search tree for package subdirs;
                          if omitted, defaults to the setup directory
__package_dirs__       -- list of subdirectories of the root of the
                          source tree that contain packages; if this is
                          omitted, any subdirectory that contains an
                          __init__.py file will be treated as a package
                          (this default should generally be sufficient)
__package_data__       -- mapping of package names to lists of data
                          files; this should generally not be needed
                          as the default package finding algorithm
                          treats any sub-directory of a package that
                          is not itself a package (i.e., doesn't have
                          an __init__.py) as being a data directory
                          (unless it's an extension module source
                          directory, see below)
__non_packages__       -- list of subdirectories of the setup directory
                          that should not be treated as packages if
                          packages are auto-detected; note that these
                          will *not* be included in source distributions
                          either (to do that, list them in __rootdirs__)

__ext_modules__        -- list of extension module objects; this should
                          not be needed, use __ext_names__
__ext_names__          -- list of names of extension modules; dotted names
                          are interpreted as modules within packages (so
                          ``foo`` is a top-level module, but ``pkg.foo`` is
                          a module in package ``pkg``); the source code for
                          each module is found by using the __ext_src__
                          variable to name a subdirectory of the extension
                          module directory (which will be the corresponding
                          source root or package directory).
__ext_src__            -- pathname to extension source files, relative to
                          the source root; if omitted, extension source files
                          will be looked for in the 'src' subdirectory of each
                          extension module directory (this should be the usual
                          case, although it is somewhat different that the
                          assumed default in the Python documentation; it
                          seems neater to keep each extension module's source
                          code near the module's own location in the build
                          tree, and difficulties that might otherwise arise
                          with doing this are avoided by SetupHelper's
                          automatically excluding extension source directories
                          from the list of packages, as noted under the
                          ``__package_data__`` variable above).

__scripts__            -- list of scripts to be included; this should
                          generally not be used, use __script_root__
                          (or the default 'scripts' directory) instead
__script_root__        -- subdir of the setup.py directory which is
                          the 'root' containing all scripts; if this
                          is omitted it will be assumed to be 'scripts'

__data_files__         -- list of data files to be included; this should
                          generally not be used, use __data_dirs__
                          instead (or the defaults)
__data_dirs__          -- list of subdirs of the setup.py directory
                          which contain data files (other than package
                          data files); if this is omitted these
                          subdirs will be checked: <progname> (if
                          it's not a package), 'examples'; data dirs
                          are installed to 'share/<progname>/<datadir>'
                          except for <progname> if it's a data dir,
                          it goes to 'lib/<progname>'.

__post_install__       -- list of script names to be run after install
                          is complete (this variable is ignored if the
                          setup command is anything other than install);
                          each name must be a valid command at a shell prompt

Note that this list of variables is for metadata version 1.1 (PEP 314);
SetupHelper supports that version even if your version of Python does
not (2.4 and earlier). Note that this applies whether or not you are
using setuptools; setuptools uses the distutils metadata support.

The setup_main function also allows you to override several of the
defaults for the SetupHelper class; the currently accepted overrides
(as keyword arguments) are:

distutils_pkg   -- package to be used in place of distutils (if omitted
                   or None, use the standard distutils; currently the
                   only other supported value is 'setuptools'); note
                   that the distutils package automatically defines
                   ext_class, requires_class, and setup_func, so these
                   are rarely needed
ext_class       -- the class to be used for extension module definitions
                   (defaults to distutils.core.Extension if using standard
                   distutils, or setuptools.extension.Extension if using
                   setuptools)
url_types       -- mapping of os.name values to download URL extensions
requires_class  -- class to be used to handle the requires keyword; defaults
                   to None if using setuptools (since setuptools.setup
                   already handles requires), or the custom RequiresHelper
                   class defined in this module for standard distutils
setup_func      -- the actual setup function to be called (defaults to
                   distutils.core.setup or setuptools.setup)

Note that each of these variables can also be defined (with two leading
and two trailing underscores) in your setup.py script; they are listed
here only because they are used internally by SetupHelper rather than to
determine the arguments passed to the actual setup function.

Any keyword arguments to setup_main besides the ones above will be treated
as keyword arguments to the actual setup function that does the work;
keyword arguments passed this way override variables set in your setup
script's globals as described above.
"""

import sys
import os
from itertools import imap, izip

SETUPHELPER_VERSION = (0, 5, 1)

def version_tuple(ver_s, dev=False):
    """
    Convert version string to tuple, correctly extracting
    an alphabetic suffix into a separate tuple item, if dev
    is False; if dev is True, returns a 2-tuple of
    <version-tuple>, <dev-tuple>
    """
    
    ver_t = ver_s.split('.')
    try:
        result = tuple(imap(int, ver_t))
        if dev:
            return (result, ())
        else:
            return result
    except ValueError:
        result = []
        for item in ver_t:
            try:
                item = int(item)
                result.append(item)
            except ValueError:
                last = ""
                for index, char in enumerate(item):
                    if char.isdigit():
                        last += char
                    else:
                        result.append(int(last))
                        dev_s = item[index:]
                        if dev:
                            result = [tuple(result), dev_tuple(dev_s)]
                        else:
                            result.append(dev_s)
                        break
        return tuple(result)

def version_string(ver_t, dev_t=None):
    """
    Convert version tuple to string, correctly handling an
    alphabetic suffix indicating a development build (at
    the end of ver_t if dev is None, else in dev).
    """
    
    try:
        result = '.'.join(imap(str, imap(int, ver_t)))
        if dev_t is not None:
            result += dev_string(dev_t)
    except ValueError:
        if dev_t is not None:
            # Should never have suffix in ver_t *and* dev_t
            raise TypeError("Version tuple contains dev build suffix.")
        result = ""
        suffix_reached = False
        for item in ver_t:
            try:
                item = int(item)
            except ValueError:
                suffix_reached = True
            if (not suffix_reached) and result:
                result += "."
            result += str(item)
    return result

# Development build string constants

alpha = 'a'
beta = 'b'
pre = 'pr'

def dev_string(dev_t):
    """
    Convert development build tuple to suffix string.
    """
    
    level, num = dev_t
    return level + str(num)

def dev_tuple(dev_s):
    """
    Convert development build suffix string to tuple.
    """
    
    level = ""
    result = (dev_s,)
    for index, char in enumerate(dev_s):
        if not char.isdigit():
            level += char
        else:
            result = (level, int(dev_s[index:]))
            break
    return result

# TODO: Remove padding of version tuples -- no need as Python tuple comparison 'just works' anyway
# (question, though: does this also apply when there is a alphabetic suffix? Or should there be
# a *different* variable to flag development builds?

def pypi_page_url(progname, version):
    """ Return the 'standard' PyPI URL for progname's page for the given version. """
    return "http://pypi.python.org/pypi/%s/%s" % (progname, version)

def pypi_source_url(progname):
    """ Return the 'standard' PyPI URL for progname's source package. """
    return "http://pypi.python.org/packages/source/%s/%s" % (progname[0], progname)

# Patch distribution metadata if Python version < 2.5 -- note that we have
# to do this whether we're using distutils or setuptools (setuptools uses
# distutils for this support anyway)

if sys.version < '2.5':
    import distutils.dist
    from distutils.dist import DistributionMetadata as _DistributionMetadata
    from distutils.util import rfc822_escape
    
    # We also need to make sure this additional metadata is registered
    # with PyPI, hence we extend the older class as Python 2.5+ does
    # (code cribbed from the 2.6 source)
    
    class DistributionMetadata(_DistributionMetadata):
        
        def __init__ (self):
            _DistributionMetadata.__init__(self)
            
            if sys.version < '2.2.3':
                self.classifiers = None
                self.download_url = None
            
            # PEP 314
            self.provides = None
            self.requires = None
            self.obsoletes = None
        
        def _write_item(self, file, name, value):
            file.write('%s: %s\n' % (name, value))
        
        def _write_list (self, file, name, values):
            for value in values:
                self._write_item(file, name, value)
        
        def write_pkg_info (self, base_dir):
            """Write the PKG-INFO file into the release tree.
            """
            
            pkg_info = open( os.path.join(base_dir, 'PKG-INFO'), 'w')
            pkg_info.write('Metadata-Version: 1.1\n')
            
            self._write_item(pkg_info, 'Name', self.get_name())
            self._write_item(pkg_info, 'Version', self.get_version())
            self._write_item(pkg_info, 'Summary', self.get_description())
            self._write_item(pkg_info, 'Home-page', self.get_url())
            self._write_item(pkg_info, 'Author', self.get_contact())
            self._write_item(pkg_info, 'Author-email', self.get_contact_email())
            self._write_item(pkg_info, 'License', self.get_license())
            if self.download_url:
                self._write_item(pkg_info, 'Download-URL', self.download_url)
            
            long_desc = rfc822_escape(self.get_long_description())
            self._write_item(pkg_info, 'Description', long_desc)
            
            keywords = ','.join(self.get_keywords())
            if keywords:
                self._write_item(pkg_info, 'Keywords', keywords)
            
            self._write_list(pkg_info, 'Platform', self.get_platforms())
            self._write_list(pkg_info, 'Classifier', self.get_classifiers())
            
            # PEP 314
            self._write_list(pkg_info, 'Requires', self.get_requires())
            self._write_list(pkg_info, 'Provides', self.get_provides())
            self._write_list(pkg_info, 'Obsoletes', self.get_obsoletes())
            
            pkg_info.close()
        
        if sys.version < '2.2.3':
            
            def get_classifiers(self):
                return self.classifiers or []
        
        # PEP 314, abbreviated from 2.6 (no set_ methods)
        
        def get_requires(self):
            return self.requires or []
        
        def get_provides(self):
            return self.provides or []
        
        def get_obsoletes(self):
            return self.obsoletes or []
    
    # Now monkeypatch distutils with our extended class
    distutils.dist.DistributionMetadata = DistributionMetadata

# Mapping of platforms to allowed archive extensions

archive_extensions = {
    'darwin': [".dmg", ".tar.gz", ".tar", ".zip"],
    'linux2': [".tar.gz", ".tar.bz2", ".zip", ".tar"],
    'win32': [".exe", ".zip", ".tar.gz", ".tar"] }

install_scripts_dir = None # see ugly hack below

# Mixin class to pretty-print Extension instances

class ExtensionMixin: # not a new-style class since Extension isn't
    """
    Mixin class adds ``__repr__`` and ``__str__`` methods to Extension
    so it will print human-readable output if the ``--verbose`` option
    is used. Note that not all of the instance variables are output,
    just the minimum to see if the instance makes sense.
    """
    
    def __repr__(self):
        return 'Extension(%r, sources=%s)' % (self.name, self.sources)
    __str__ = __repr__

def distutils_default():
    """ Support function for Python-provided distutils. """
    
    import distutils.command.install_scripts
    from distutils.command.install_scripts import install_scripts as _install_scripts
    from distutils.core import setup, Extension
    import urllib2
    import re
    
    class install_scripts(_install_scripts):
        """
        Captures the script installation directory so that post-install scripts
        will be run correctly. Yes, this is an ugly hack; if distutils would
        expose these directories to setup scripts all this would be unnecessary.
        """
        
        def finalize_options(self):
            global install_scripts_dir
            _install_scripts.finalize_options(self)
            install_scripts_dir = self.install_dir
            print "Installing scripts to %s ..." % install_scripts_dir
    
    # Monkeypatch distutils with our hacked class above
    distutils.command.install_scripts.install_scripts = install_scripts
    
    class RequiresHelper(object):
        """
        Helper class to handle requires keyword. Should be
        instantiated with a list of strings suitable for the
        # requires variable/keyword.
        """
        
        # TODO: add a command line option to specify a different repository base URL
        pypi_url = "http://pypi.python.org/simple/"
        user_agent = "Python-urllib/%s SetupHelper/%s" % (
            urllib2.__version__, SETUPHELPER_VERSION)
        
        # NOTE: this is *not* fully general URL detection and parsing; it only
        # does the minimum necessary to work with HTML pages like those on PyPI
        # that contain properly formatted URLs within relatively "clean" content
        
        p_scheme = r"(https?|ftp):\/\/"
        p_hostname = r"([a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*)"
        p_portspec = r"(:[0-9]+)?"
        p_pathname = r"(\/[a-zA-Z0-9._%/\-]*)?"
        p_params = r"(;[a-zA-Z0-9._%/=\-]*)?"
        p_query = r"(\?[a-zA-Z0-9._%/=\-]*)?"
        p_fragment = r"(#[a-zA-Z0-9._%/=\-]*)?"
        
        url_pattern = p_scheme + p_hostname + p_portspec + p_pathname \
            + p_params + p_query + p_fragment
        href_pattern = r"\<a href\=\'" + url_pattern + r"\'\>"
        
        # If there is a variable PYPI_LOCAL in the environment, it should point
        # to a local directory that can store source archives; we'll look in it
        # to avoid downloads if possible
        
        pypi_local = os.getenv('PYPI_LOCAL')
        
        class URLMatchObject(object):
            """ Wrapper object for convenience in handling URL matches. """
            
            def __init__(self, m):
                self.__m = m
                self.url = m.group()
                self.scheme, self.hostname, self.domain, self.portspec, self.pathname, \
                    self.params, self.query, self.fragment = m.groups()
        
        try:
            allowed_extensions = archive_extensions[sys.platform]
        except KeyError:
            allowed_extensions = ["tar.gz", ".zip"] # reasonably safe choice
        
        def __init__(self, requires, opts, debug=False):
            self._requires = requires
            self._debug = debug
            
            self.setup_opts = opts
            self.srcdir = ""
        
        def find_pattern(data, pattern, klass=None):
            r = re.compile(pattern)
            if klass is None:
                return r.finditer(data)
            else:
                def i():
                    for m in r.finditer(data):
                        yield klass(m)
                return i()
        find_pattern = staticmethod(find_pattern)
        
        def find_urls(self, data):
            """ Return an iterator that yields a URLMatchObject for each URL in data. """
            return self.find_pattern(data, self.url_pattern, self.URLMatchObject)
        
        def find_hrefs(self, data):
            return self.find_pattern(data, self.href_pattern, self.URLMatchObject)
        
        def archive_pattern(self, progname):
            """ Return regexp pattern for archive filenames for progname. """
            return progname + r"\-([0-9][a-zA-Z0-9._\-]*)(.tar(.gz|.bz2)?|.zip|.exe|.dmg)$"
        
        def version_tuple(verstr, length=4):
            """ Return tuple of version numbers, padded with -1 to length to make sorting easier. """
            t = verstr.split('.')
            return tuple(imap(int, t) + [-1]*(length - len(t)))
        version_tuple = staticmethod(version_tuple)
        
        def find_archives_in_iterable(self, iterable, progname):
            result = []
            r = re.compile(self.archive_pattern(progname))
            elist = self.allowed_extensions
            e = len(elist)
            for item in iterable:
                if isinstance(item, tuple):
                    # Unpack if being called from find_archives
                    item, url = item
                else:
                    url = None
                fname = r.search(item)
                if fname is not None:
                    filename = fname.group()
                    version, ext, subext = fname.groups()
                    i = elist.index(ext)
                    if i > -1:
                        result.append((self.version_tuple(version), e - i,
                            url, ext, filename, version))
            return result
        
        def find_archives(self, data, progname, hrefs=False):
            """
            Return a list of 6-tuples, one for each archive URL for progname found in data.
            Each tuple contains <version-tuple>, <index>, <url>, <extension>, <filename>, where:
            
            <version-tuple> is the tuple of version numbers for sorting;
            
            <index> is the (inverse) index of the extension in the list of allowed extensions
            (it's inverted so that when we reverse sort, the preferred extension is first);
            
            <url> is the download URL;
            
            <extension> is the archive extension (used to determine its type);
            
            <filename> is the filename to be used to save the archive locally;
            
            <version> is the version string.
            
            If the hrefs parameter is true, only find URLs embedded in href tags. This
            is usually not necessary, hence defaults to False.
            """
            
            if hrefs:
                f = self.find_hrefs
            else:
                f = self.find_urls
            return self.find_archives_in_iterable(
                ((m.pathname, m.url) for m in f(data) if m.pathname is not None),
                progname)
        
        def latest_sorted_version(self, versions):
            if versions:
                versions.sort() # sorts by version tuple, then inverse index
                versions.reverse() # puts the latest at the top
                return versions[0]
            return None
        
        def get_latest_version(self, data, progname, spec, hrefs=False):
            """
            Return the tuple for the latest version of progname, with the most
            preferred archive type if more than one is available of that version.
            If no archive with an allowed extension is found, print an error
            message and return None.
            """
            
            # TODO: incorporate spec into logic
            versions = self.find_archives(data, progname, hrefs)
            return self.latest_sorted_version(versions)
        
        def download_url(self, url):
            request = urllib2.Request(url)
            request.add_header('User-Agent', self.user_agent)
            data = None
            try:
                f = urllib2.urlopen(request)
                try:
                    data = f.read()
                finally:
                    f.close()
            except urllib2.URLError:
                pass
            return data
        
        def find_local_archives(self, req, srcdir):
            if os.path.isdir(srcdir):
                versions = self.find_archives_in_iterable(os.listdir(srcdir),
                    req)
                return self.latest_sorted_version(versions)
            return None
        
        def get_latest_local_version(self, req, spec, clean=False):
            # TODO: incorporate spec into logic
            result = None
            if self.pypi_local and not clean:
                # Check for a local repository; we assume that pypi_local
                # points to a repository directory
                for srcdir in (self.pypi_local, os.path.join(self.pypi_local, req)):
                    local = self.find_local_archives(req, srcdir)
                    if local is not None:
                        if (result is None) or (local[:2] > result[:2]):
                            result = local
                            self.srcdir = srcdir
            return result
        
        def process_req(self, req, spec, latest_local, link_data=None, clean=False):
            if (link_data is not None) and (not clean):
                # Find latest online version and url by looking in link_data
                latest = self.get_latest_version(link_data, req, spec)
            else:
                latest = None
            
            if (latest_local is not None) and ((latest is None) or (latest_local[:2] >= latest[:2])):
                latest = latest_local
            
            # See if we have at least one usable archive; if not, bail
            if (latest is None) and not clean:
                print >>sys.stderr, "Could not find a usable archive for %s." % progname
                return
            
            if not clean:
                # Unpack the latest version info
                ver_tuple, index, url, ext, filename, version = latest
                
                # Get archive extension and determine commands and options
                if ext.startswith(".tar"):
                    try:
                        opts = {'.gz': 'z', '.bz2': 'j'}[ext[4:]]
                    except KeyError:
                        opts = ""
                    unpack_cmd = "tar -x%svf" % opts
                elif ext == ".zip":
                    unpack_cmd = "unzip"
                else:
                    unpack_cmd = ""
                
                # Determine archive status, and download/copy if needed
                depfilename = os.path.join("deps", filename)
                if os.path.isfile(depfilename):
                    print filename, "was previously downloaded."
                else:
                    data = None
                    if url is None:
                        # This was a local archive, so construct its full filename
                        srcfilename = os.path.join(self.srcdir, filename)
                        if os.path.isfile(srcfilename):
                            # Copy the data from the local file
                            print filename, "is in local repository, copying."
                            srcfile = open(srcfilename, 'rb')
                            try:
                                data = srcfile.read()
                            finally:
                                srcfile.close()
                    else:
                        # Download actual archive data and save it locally
                        print "Downloading", filename
                        data = self.download_url(url)
                    if data is not None:
                        if not os.path.isdir("deps"):
                            os.mkdir("deps")
                        depfile = open(depfilename, 'wb')
                        try:
                            depfile.write(data)
                        finally:
                            depfile.close()
            
            # Save current working directory so we can return when done
            setup_dir = os.getcwd()
            
            if os.path.isdir("deps"):
                os.chdir("deps")
                
                if not clean:
                    if unpack_cmd:
                        # Unpack the source archive in the deps directory
                        unpack_dir = "%s-%s" % (req, version)
                        if os.path.isdir(unpack_dir):
                            print unpack_dir, "was previously unpacked."
                        else:
                            unpack_cmdline = "%s %s" % (unpack_cmd, filename)
                            print "Executing", unpack_cmdline
                            os.system(unpack_cmdline)
                    elif "install" in self.setup_opts:
                        # The archive can be executed directly (exe), but we only
                        # do this if we're installing
                        print "Executing", filename
                        os.system(filename)
                        unpack_dir = None
                else:
                    unpack_dir = None
                    for dname in os.listdir("."):
                        if os.path.isdir(dname) and dname.startswith(req):
                            unpack_dir = dname
                            break
                
                # Chdir to the source root and run setup with same args as ours
                if unpack_dir and os.path.isdir(unpack_dir):
                    os.chdir(unpack_dir)
                    process_cmdline = "python setup.py %s" % self.setup_opts
                    print "Executing", process_cmdline
                    os.system(process_cmdline)
                
                os.chdir(setup_dir)
            
            print "Processed requirement %s." % req
        
        def process_reqs(self):
            """
            Resolve each requirement in requires list. The debug
            flag, if True, saves the downloaded html data from
            PyPI and each requirement's download page, for use
            in analyzing what's going on.
            """
            
            # Determine if we're running setup.py clean
            clean = ("clean" in self.setup_opts)
            
            # Grab the PyPI simple index data
            pypi_data = self.download_url(self.pypi_url)
            if self._debug:
                self._pypi_data = pypi_data
                self._req_data = {}
            if pypi_data is not None:
                # Now process the requirements
                for req in self._requires:
                    # TODO: Strip version specifier off end and store
                    spec = None
                    
                    # First try to import it -- assumes req is an importable name
                    # (we don't do this if cleaning because we may want to clean
                    # a previously build deps directory)
                    if not clean:
                        try:
                            __import__(req)
                            print "Requirement %s found, no processing needed." % req
                            continue
                        except ImportError:
                            pass
                    
                    # Next look in PyPI for it -- assumes req is a PyPI name
                    findstr = "<a href='%s/'>" % req
                    link_data = None
                    if findstr in pypi_data:
                        # Found it, load its link page
                        link_data = self.download_url('%s%s/' %
                            (self.pypi_url, req))
                        if link_data is not None:
                            if self._debug:
                                self._req_data[req] = link_data
                    
                    # Check local repository if there is one
                    latest_local = self.get_latest_local_version(req, spec, clean)
                    
                    if (link_data is not None) or (latest_local is not None):
                        print "Processing requirement %s..." % req
                        self.process_req(req, spec, latest_local, link_data, clean)
                        continue
                    
                    # If we get here, requirement was not found
                    print >>sys.stderr, \
                        "Could not find requirement %s; program may not run." % req
    
    class SHExtension(ExtensionMixin, Extension):
        pass
    
    def setup_wrapper(**kwargs):
        """ Wrapper for distutils setup function. """
        if 'name' in kwargs:
            setup(**kwargs)
    
    return (RequiresHelper, SHExtension, setup_wrapper)

def distutils_setuptools():
    """ Support function for setuptools. """
    
    # Make use of ez_setup optional -- if it's not present, assume that
    # the packager has ensured setuptools support by some other method
    try:
        from ez_setup import use_setuptools
        use_setuptools()
    except ImportError:
        pass
    
    from setuptools import setup
    from setuptools.extension import Extension
    
    class SHExtension(ExtensionMixin, Extension):
        pass
    
    def setup_wrapper(**kwargs):
        """ Wrapper for setuptools setup function. """
        if 'name' in kwargs:
            setup(**kwargs)
        elif 'install_requires' in kwargs:
            from setuptools.command.easy_install import main
            sys.argv[0] = "easy_install"
            opts = sys.argv[1:]
            for req in kwargs['install_requires']:
                main([req] + opts)
    
    return (None, SHExtension, setup_wrapper)

# This will be used to process the __license__ variable below

license_map = dict(izip(
    ("PSF", "GNU GPL"), """
License :: OSI Approved :: Python Software Foundation License
License :: OSI Approved :: GNU General Public License (GPL)
""".strip().splitlines()))

# This will be used to process the __dev_status__ variable below;
# note that we order the items to ensure a unique match if the
# status string happens to contain 'Alpha' but not 'Pre-Alpha'

devstatus_trove = """
Development Status :: 3 - Alpha
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Development Status :: 6 - Mature
Development Status :: 7 - Inactive
Development Status :: 1 - Planning
Development Status :: 2 - Pre-Alpha
""".strip().splitlines()

class SetupHelper(object):
    """ Helper class to manage setup process. """
    
    setup_vars = [
        'setup_main',
        'SetupHelper',
        '__setup_func__',
        '__setup_args__',
        '__post_install__' ]
    
    python_builtins = [
        '__builtins__',
        '__doc__',
        '__file__',
        '__name__',
        '__package__' ]
    
    overrides = [
        'distutils_pkg',
        'url_types' ]
    
    metavars = [
        'ext_class',
        'requires_class',
        'setup_func' ]
    
    dirsep = '/'
    pkgsep = '.'
    
    verbose = False
    
    def dir_to_os(self, dirname):
        """ Converts distutils dirname to os dirname. """
        return os.path.join(*dirname.split(self.dirsep))
    
    def dir_to_pkg(self, dirname):
        """ Converts relative directory path into dotted package name. """
        return dirname.replace(self.dirsep, self.pkgsep)
    
    def os_to_dir(self, dirname):
        """ Converts os directory path into distutils dirname. """
        return dirname.replace(os.sep, self.dirsep)
    
    def os_to_pkg(self, dirname):
        """ Converts os directory path into dotted package name. """
        return dirname.replace(os.sep, self.pkgsep)
    
    def pkg_to_dir(self, pkgname):
        """ Converts dotted package name into relative directory path. """
        return pkgname.replace(self.pkgsep, self.dirsep)
    
    def pkg_to_os(self, pkgname):
        """ Converts dotted package name to os dirname. """
        return os.path.join(*pkgname.split(self.pkgsep))
    
    def search_classifiers(self, s):
        """
        Search classifiers for one that contains a given string. Used
        to see if classifiers already contain license or dev status.
        """
        s = s + ' ::'
        for item in self.__classifiers__:
            if s in item:
                return True
        return False
    
    def __init__(self, vars, **kwargs):
        # Store list of internal variables so we don't merge them
        # into setup args later
        internal_vars = dir(self)
        
        # Add variables that might be imported by the setup.py script
        # (because they'll show up in vars) and that we'll generate
        # (or won't erase) but will not want as keyword args to setup
        internal_vars.extend(self.setup_vars)
        
        # First transfer variables to our __dict__ from above args
        self.init_vars(vars, kwargs)
        
        # Now process variables from setup.py (we check for a __progname__
        # first because if it isn't there, we assume we were called from
        # the setuphelper script and only need to do requires processing
        if hasattr(self, '__progname__'):
            self.process_readme()
            self.process_vars()
            self.write_manifest()
            self.process_metadata()
        
        # Now do the requires processing
        self.process_requires()
        
        # Now merge the rest of the variables into the setup args; note
        # that we merge instead of updating so that keyword arguments
        # passed to the setup script override variables set in its globals
        for varname in dir(self):
            if varname not in internal_vars:
                if varname == '__progname__':
                    # Special case this one, we can't use __name__ because it is
                    # a special Python variable for modules already
                    setup_arg = 'name'
                else:
                    # Strip the leading and trailing underscores
                    setup_arg = varname.strip('_')
                if setup_arg not in self.__setup_args__:
                    self.__setup_args__[setup_arg] = getattr(self, varname)
    
    def init_vars(self, vars, kwargs):
        # First remove overrides that won't be used if we're being
        # called from the setuphelper script
        overrides = self.overrides[:]
        metavars = self.metavars[:]
        if '__progname__' not in vars:
            overrides.remove('url_types')
            metavars.remove('ext_class')
        
        # Process overrides passed in keyword arguments
        for varname in (overrides + metavars):
            attrname = '__%s__' % varname
            value = kwargs.pop(varname, None)
            if (value is not None) or (attrname not in vars):
                vars[attrname] = value
        
        # Now get the setup variables passed to us by the setup script
        # (plus any overrides that were written in above)
        for varname, value in vars.iteritems():
            # Don't change the Python-provided vars
            if varname not in self.python_builtins:
                setattr(self, varname, value)
        
        # Set defaults by distutils package
        if self.__distutils_pkg__ is None:
            self.__distutils_pkg__ = 'default'
        requires_class, ext_class, setup_func = getattr(sys.modules[__name__],
            'distutils_%s' % self.__distutils_pkg__)()
        del self.__distutils_pkg__
        # We only set variables that weren't already set above
        for varname in metavars:
            attrname = '__%s__' % varname
            if getattr(self, attrname) is None:
                setattr(self, attrname, locals()[varname])
        
        # The keyword args left over are treated as keyword args for the
        # setup function below
        self.__setup_args__ = dict(kwargs)
    
    def process_readme(self):
        # crib our long description from the opening section of
        # the README file
        if hasattr(self, '__start_line__') or hasattr(self, '__end_line__'):
            if not hasattr(self, '__long_description__'):
                for attrname in ('__start_line__', '__end_line__'):
                    if not hasattr(self, attrname):
                        setattr(self, attrname, None)
                
                if isinstance(self.__start_line__, int):
                    startline = self.__start_line__
                elif self.__start_line__ is None:
                    startline = 0
                else:
                    startline = None
                if isinstance(self.__end_line__, int):
                    endline = self.__end_line__
                else:
                    endline = None
                
                readme = open("README", 'rU')
                try:
                    lines = readme.readlines()
                finally:
                    readme.close()
                
                if (endline is not None) and (endline < 0):
                    endline = endline + len(lines)
                desclines = []
                started = False
                for lineno, line in enumerate(lines):
                    line = line.rstrip('\n')
                    if started:
                        if (lineno == endline) or (line == self.__end_line__):
                            break
                        else:
                            desclines.append(line)
                    elif (lineno == startline) or (line == self.__start_line__):
                        desclines.append(line)
                        started = True
                
                self.__long_description__ = '\n'.join(desclines)
            
            for attrname in ('__start_line__', '__end_line__'):
                if hasattr(self, attrname):
                    delattr(self, attrname)
    
    def process_vars(self):
        # We'll store the lines that need to go into MANIFEST.in here (and add
        # more below if applicable) -- note the special-casing of SetupHelper.py
        # depending on whether it is explicitly listed in py_modules or packages
        self.__manifest_in__ = []
        if not hasattr(self, '__rootfiles__'):
            if hasattr(self, '__py_modules__') and ('SetupHelper' in self.__py_modules__):
                self.__rootfiles__ = []
            else:
                self.__rootfiles__ = ["SetupHelper.py"]
        if not hasattr(self, '__rootdirs__'):
            if hasattr(self, '__packages__') and ('SetupHelper' in self.__packages__):
                self.__rootdirs__ = []
            else:
                self.__rootdirs__ = ["SetupHelper"]
        for rootfile in self.__rootfiles__:
            # Include glob patterns without checking for file existence
            if os.path.isfile(rootfile) or ('*' in rootfile) or ('?' in rootfile):
                self.__manifest_in__.append("include %s\n" % rootfile)
        for rootdir in self.__rootdirs__:
            if os.path.isdir(rootdir):
                self.__manifest_in__.append("recursive-include %s *.*\n" % rootdir)
                if rootdir == "SetupHelper":
                    # Don't include the byte-compiled module in source distributions
                    # (it will always be there because it had to be imported for this
                    # code to run!)
                    self.__manifest_in__.append("recursive-exclude SetupHelper *.pyc\n")
        
        # Figure out the root of the source tree
        if hasattr(self, '__package_dir__') and ('' in self.__package_dir__):
            self.__package_root__ = self.__package_dir__['']
        elif not hasattr(self, '__package_root__'):
            self.__package_root__ = "."
        
        # Figure out the pure Python modules list
        if not hasattr(self, '__non_modules__'):
            self.__non_modules__ = []
        if not hasattr(self, '__py_modules__'):
            self.__py_modules__ = [entry[:-3] for entry in os.listdir(self.__package_root__)
                if entry.endswith(".py") and (entry != "setup.py")
                    and (entry not in self.__non_modules__)
                    and (entry not in self.__rootfiles__)]
        if not self.__py_modules__:
            del self.__py_modules__
        del self.__non_modules__
        del self.__rootfiles__
        
        # Figure out the extension modules list (do this first so we can filter
        # out extension directories from the package data list below)
        if not hasattr(self, '__ext_modules__'):
            self.__ext_modules__ = []
        self.__ext_sourcedirs__ = []
        if hasattr(self, '__ext_names__'):
            if hasattr(self, '__ext_src__'):
                ext_src_func = lambda extname: self.__ext_src__
            else:
                ext_src_func = lambda extname: os.path.normpath(
                    os.path.join(os.path.split(self.pkg_to_os(extname))[0], 'src'))
            for extname in self.__ext_names__:
                srcdir = ext_src_func(extname)
                if os.path.isdir(srcdir):
                    self.__ext_modules__.append(self.__ext_class__(extname,
                        sources=[self.os_to_dir(os.path.join(srcdir, filename))
                            for filename in os.listdir(srcdir) if filename.endswith(".c")]))
                    self.__ext_sourcedirs__.append(srcdir)
            if hasattr(self, '__ext_src__'):
                del self.__ext_src__
            del self.__ext_names__
        # TODO: if __ext_modules__ exists but no __ext_names__, parse it to
        # populate __ext_sourcedirs__
        if not self.__ext_modules__:
            del self.__ext_modules__
        del self.__ext_class__
        
        # Figure out the package and package_data lists
        if hasattr(self, '__packages__'):
            process_packages = False
        else:
            self.__packages__ = []
            process_packages = True
        if hasattr(self, '__package_data__'):
            process_packagedata = False
        else:
            self.__package_data__ = {}
            process_packagedata = True
        if not hasattr(self, '__package_dirs__'):
            if not process_packages:
                self.__package_dirs__ = [p for p in self.__packages__
                    if "." not in p]
            #elif hasattr(self, '__package_dir__'):
            #    self.__package_dirs__ = [k for k in self.__package_dir__.keys()
            #        if k] # filters out the empty string if present
            else:
                self.__package_dirs__ = [entry for entry in os.listdir(self.__package_root__)
                    if os.path.isdir(entry) and ("__init__.py" in os.listdir(entry))
                        and (entry not in self.__rootdirs__)]
        del self.__rootdirs__
        if process_packages or process_packagedata:
            for pkgdir in self.__package_dirs__:
                for directory, subdirs, files in os.walk(pkgdir):
                    if process_packages and ("__init__.py" in files):
                        self.__packages__.append(self.os_to_pkg(directory))
                    elif process_packagedata and ("." not in directory) \
                        and (directory not in self.__ext_sourcedirs__):
                            parentdir, thisdir = os.path.split(directory)
                            pkg = self.os_to_pkg(parentdir)
                            pkgdir = self.os_to_dir(directory)
                            if not pkg in self.__package_data__:
                                self.__package_data__[pkg] = []
                            self.__package_data__[pkg].append("%s%s*.*" % (thisdir, self.dirsep))
                            self.__manifest_in__.append("recursive-include %s *.*\n" % pkgdir)
        if not self.__packages__:
            del self.__packages__
        if not self.__package_data__:
            del self.__package_data__
        del self.__package_root__
        del self.__ext_sourcedirs__
        
        # Figure out the scripts and data_files lists
        # NOTE: The extra jugglery with not "." in dirname and filename.startswith(".") is to mask
        # out hidden files and directories -- without this running setup from an svn working copy
        # goes haywire because it thinks that all the svn hidden files are scripts or data files
        if not hasattr(self, '__scripts__'):
            self.__scripts__ = []
            if not hasattr(self, '__script_root__'):
                self.__script_root__ = "scripts"
            if os.path.isdir(self.__script_root__):
                for directory, subdirs, files in os.walk(self.__script_root__):
                    if "." not in directory:
                        scriptdir = self.os_to_dir(directory)
                        for filename in files:
                            if not filename.startswith("."):
                                self.__scripts__.append("%s%s%s" % (scriptdir, self.dirsep, filename))
        if hasattr(self, '__script_root__'):
            del self.__script_root__
        if not hasattr(self, '__data_files__'):
            self.__data_files__ = []
            if not hasattr(self, '__data_dirs__'):
                self.__data_dirs__ = ["examples"]
                if (self.__progname__ not in self.__package_dirs__):
                    self.__data_dirs__.append(self.__progname__)
            for datadir in self.__data_dirs__:
                if os.path.isdir(datadir):
                    if datadir == self.__progname__:
                        pathprefix = "lib"
                    else:
                        pathprefix = "share%s%s" % (self.dirsep, self.__progname__)
                    for directory, subdirs, files in os.walk(datadir):
                        if files and ("." not in directory):
                            distdir = self.os_to_dir(directory)
                            self.__data_files__.append(("%s%s%s" % (pathprefix, self.dirsep, distdir),
                                ["%s%s%s" % (distdir, self.dirsep, filename) for filename in files
                                    if not filename.startswith(".")]))
                    self.__manifest_in__.append("recursive-include %s *.*\n" % datadir)
        if not self.__scripts__:
            del self.__scripts__
        if not self.__data_files__:
            del self.__data_files__
        if hasattr(self, '__data_dirs__'):
            del self.__data_dirs__
        del self.__package_dirs__
    
    def write_manifest(self):
        # Write MANIFEST.in -- tmp file first so we don't clobber the current
        # one if there's a problem
        manifest_in = open("MANIFEST.in.tmp", 'w')
        try:
            manifest_in.writelines(self.__manifest_in__)
        finally:
            manifest_in.close()
        if os.path.isfile("MANIFEST.in"):
            os.rename("MANIFEST.in", "MANIFEST.in.old")
        os.rename("MANIFEST.in.tmp", "MANIFEST.in")
        if os.path.isfile("MANIFEST.in.old"):
            os.remove("MANIFEST.in.old")
        del self.__manifest_in__
    
    def process_metadata(self):
        # If version is a tuple, convert to a string (need to do this before
        # the URLs are determined)
        if isinstance(self.__version__, tuple):
            self.__version__ = version_string(self.__version__)
        
        # Determine project URL -- assume PyPI if none given
        if not hasattr(self, '__url__'):
            self.__url__ = pypi_page_url(self.__progname__, self.__version__)
        
        # Determine download URL -- assume the base is the PyPI source URL
        # if no base is given
        if not hasattr(self, '__url_base__'):
            self.__url_base__ = pypi_source_url(self.__progname__)
        if not hasattr(self, '__url_ext__'):
            if not hasattr(self, '__url_type__'):
                self.__url_ext__ = 'tar.gz'
            else:
                if self.__url_types__ is None:
                    self.__url_types__ = {'posix': "tar.gz", 'nt': "zip"}
                try:
                    self.__url_ext__ = self.__url_types__[self.__url_type__]
                except KeyError:
                    self.__url_ext__ = self.__url_type__
                del self.__url_type__
        self.__download_url__ = "%s/%s-%s.%s" % (
            self.__url_base__, self.__progname__, self.__version__, self.__url_ext__)
        del self.__url_types__
        del self.__url_base__
        del self.__url_ext__
        
        # Convert classifiers from long string to list
        if hasattr(self, '__classifiers__'):
            if isinstance(self.__classifiers__, basestring):
                self.__classifiers__ = self.__classifiers__.strip().splitlines()
        else:
            self.__classifiers__ = []
        
        # Fill in license classifier if none present and license is defined;
        # this allows us to discard the __license__ variable (PyPI says it
        # shouldn't be used if there's a classifer present)
        has_license = self.search_classifiers('License')
        if hasattr(self, '__license__'):
            if not has_license:
                if self.__license__ in license_map:
                    self.__classifiers__.append(license_map[self.__license__])
                    has_license = True
            if has_license:
                del self.__license__
        
        # Fill in dev_status classifier from __dev_status__ if present
        if hasattr(self, '__dev_status__'):
            has_status = self.search_classifiers('Development Status')
            if not has_status:
                devstatus = self.__dev_status__.lower()
                for trove in devstatus_trove:
                    if (devstatus in trove.lower()):
                        self.__classifiers__.append(trove)
                        break
            del self.__dev_status__
        
        # Sort classifiers (not necessary, but looks better)
        self.__classifiers__.sort()
    
    def process_requires(self):
        # Grab setup options from our sys.argv so we can use the same
        # ones when processing requirements
        setup_opts = " ".join([opt for opt in sys.argv[1:] if opt not in ("python", "setup.py")])
        
        if hasattr(self, '__progname__'):
            # Check to see if we need to even process requirements
            do_requires = False
            for cmd in ("build", "clean", "install"):
                if cmd in setup_opts:
                    do_requires = True
                    break
        else:
            # If no progname, we're being called by setuphelper, always do requires,
            # and prefix "install" to setup options
            setup_opts = "install %s" % setup_opts
            do_requires = True
        
        if hasattr(self, '__install_requires__'):
            # We need to copy the variable name here so it will show up in PKG-INFO
            # (we can't use __requires__ in the setup script because that breaks setuptools)
            self.__requires__ = self.__install_requires__
            if self.__requires_class__ is not None:
                # Process requires keyword if not using setuptools (in setuptools calling
                # the setup_func takes care of this); this is the last thing we do before
                # merging arguments and calling setup
                if do_requires:
                    self.__requires_class__(self.__install_requires__, setup_opts).process_reqs()
                # We can now delete this variable since it's not used in standard distutils
                del self.__install_requires__
        del self.__requires_class__
    
    def do_setup(self):
        """
        This does the actual work; we separate it out to allow hooking into
        the process after the setup args are parsed above but before the
        function call.
        """
        
        if self.verbose:
            for key, value in self.__setup_args__.iteritems():
                print key, '=', value
        self.__setup_func__(**self.__setup_args__)
    
    def do_post_install(self):
        """
        This runs any post-install scripts that are defined; again, we
        separate this out to allow hooking after the install but before
        the post-install scripts run.
        """
        
        if hasattr(self, '__post_install__') and self.__post_install__:
            print "Running post-install scripts in %s ..." % install_scripts_dir
            for scriptname in self.__post_install__:
                # Use ugly hack above to get script dir from distutils to be sure we're grabbing the right script
                os.system(os.path.join(install_scripts_dir, scriptname))

# TODO: convert long option of the form --<option-name>=<value> to keyword argument option_name=value

def setup_main(vars, **kwargs):
    helper = SetupHelper(vars, **kwargs)
    for opt in ('-v', '--verbose'):
        if opt in sys.argv:
            sys.argv.remove(opt)
            helper.verbose = True
    helper.do_setup()
    if 'install' in sys.argv:
        helper.do_post_install()
