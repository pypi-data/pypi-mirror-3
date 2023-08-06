"""
package model for python PAckage INTrospection
"""

# TODO: use pkginfo.sdist more

import os
import pip
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib2
import urlparse
import utils

try:
    from subprocess import check_call as call
except ImportError:
    from subprocess import call

__all__ = ['Package']

class Package(object):
    """
    class for python package introspection.
    constructor takes the package 'src'
    """

    def __init__(self, src):
        self.src = src

        # ephemeral data
        self._tmppath = None
        self._egg_info_path = None
        self._build_path = None
        self._pkg_info_path = None

        # TODO: list of temporary files/directories to be deleted

    def _path(self):
        """filesystem path to package directory"""

        # return cached copy if it exists
        if self._tmppath:
            return self._tmppath

        # fetch from the web if a URL
        tmpfile = None
        src = self.src
        if utils.isURL(self.src):
            tmpfile = src = self.fetch()

        # unpack if an archive
        if self._is_archive(src):
            try:
                self._unpack(src)
            finally:
                if tmpfile:
                    os.remove(tmpfile)
            return self._tmppath

        return self.src

    def fetch(self, filename=None):
        """fetch from remote source to a temporary file"""
        if filename is None:
            fd, filename = tempfile.mkstemp()
            os.close(fd)
        fp = file(filename, 'w')
        resource = urllib2.urlopen(self.src)
        fp.write(resource.read())
        fp.close()
        return filename

    def _unpack(self, archive):
        """unpack the archive to a temporary destination"""
        # TODO: should handle zipfile additionally at least
        # Ideally, this would be pluggable, etc
        assert tarfile.is_tarfile(archive), "%s is not an archive" % self.src
        tf = tarfile.TarFile.open(archive)
        self._tmppath = tempfile.mkdtemp()
        members = tf.getmembers()

        # cut off the top level directory
        members = [i for i in members if os.path.sep in i.name]
        tld = set()
        for member in members:
            directory, member.name = member.name.split(os.path.sep, 1)
            tld.add(directory)
        assert len(tld) == 1

        # extract
        for member in members:
            tf.extract(member, path=self._tmppath)
        tf.close()

    def _is_archive(self, path):
        """returns if the filesystem path is an archive"""
        # TODO: should handle zipfile additionally at least
        # Ideally, this would be pluggable, etc
        return tarfile.is_tarfile(path)

    def _cleanup(self):
        if self._tmppath:
            shutil.rmtree(self._tmppath)
        self._tmppath = None

#    __del__ = cleanup

    ### python-package-specific functionality

    def _egg_info(self):
        """build the egg_info directory"""

        if self._egg_info_path:
            # return cached copy
            return self._egg_info_path

        directory = self._path()
        setup_py = os.path.join(directory, 'setup.py')
        if not os.path.exists(setup_py):
            raise AssertionError("%s does not exist" % setup_py)

        # setup the egg info
        exception = None
        try:
            code = call([sys.executable, 'setup.py', 'egg_info'], cwd=directory, stdout=subprocess.PIPE)
        except BaseException, exception:
            pass
        if code or exception:
            message = """Failure to generate egg_info
- src: %s
- directory: %s
""" % (self.src, directory)
            if exception:
                sys.stderr.write(message)
                raise exception
            else:
                raise Exception(message)

        # get the .egg-info directory
        egg_info = [i for i in os.listdir(directory)
                    if i.endswith('.egg-info')]
        assert len(egg_info) == 1, 'Expected one .egg-info directory in %s, got: %s' % (directory, egg_info)
        egg_info = os.path.join(directory, egg_info[0])
        assert os.path.isdir(egg_info), "%s is not a directory" % egg_info

        # cache it
        self._egg_info_path = egg_info
        return self._egg_info_path

    def _pkg_info(self):
        """returns path to PKG-INFO file"""

        if self._pkg_info_path:
            # return cached value
            return self._pkg_info_path

        try:
            egg_info = self._egg_info()
        except BaseException, exception:
            # try to get the package info from a file
            path = self._path()
            pkg_info = os.path.join(path, 'PKG-INFO')
            if os.path.exists(pkg_info):
                self._pkg_info_path = pkg_info
                return self._pkg_info_path
            raise Exception("Cannot find or generate PKG-INFO")

        pkg_info = os.path.join(egg_info, 'PKG-INFO')
        assert os.path.exists(pkg_info)
        self._pkg_info_path = pkg_info
        return self._pkg_info_path

    def info(self):
        """return info dictionary for package"""
        # could use pkginfo module

        pkg_info = self._pkg_info()

        # read the package information
        info_dict = {}
        for line in file(pkg_info).readlines():
            if not line or line[0].isspace():
                continue # XXX neglects description
            assert ':' in line
            key, value = [i.strip() for i in line.split(':', 1)]
            info_dict[key] = value

        # return the information
        return info_dict

    def dependencies(self):
        """return the dependencies"""
        # TODO: should probably have a more detailed dict:
        # {'mozinfo': {'version': '>= 0.2',
        #              'url': 'http://something.com/'}}
        # get the egg_info directory
        egg_info = self._egg_info()

        # read the dependencies
        requires = os.path.join(egg_info, 'requires.txt')
        if os.path.exists(requires):
            dependencies = [i.strip() for i in file(requires).readlines() if i.strip()]
        else:
            dependencies = []
        dependencies = dict([(i, None) for i in dependencies])

        # read the dependency links
        dependency_links = os.path.join(egg_info, 'dependency_links.txt')
        if os.path.exists(dependency_links):
            links = [i.strip() for i in file(dependency_links).readlines() if i.strip()]
            for link in links:
                # XXX pretty ghetto
                assert '#egg=' in link
                url, dep = link.split('#egg=', 1)
                if dep in dependencies:
                    dependencies[dep] = link

        return dependencies

    def extension(self):
        """filename extension of the package"""

        package = self.package()

        # determine the extension (XXX hacky)
        extensions = ('.tar.gz', '.zip', '.tar.bz2')
        for ext in extensions:
            if package.endswith(ext):
                return ext

        raise Exception("Extension %s not found: %s" % (extensions, package))

    def package(self, destination=None):
        """
        repackage the package to ensure its actually in the right form
        and return the path to the destination
        - destination: if given, path to put the build in [TODO]
        """

        if self._build_path:
            if destination:
                shutil.copy(self._build_path, destination)
                return os.path.abspath(destination)

            # return cached copy
            return self._build_path

        path = self._path()
        dist = os.path.join(path, 'dist')
        if os.path.exists(dist):
            shutil.rmtree(dist)

        call([sys.executable, 'setup.py', 'sdist'], cwd=path, stdout=subprocess.PIPE)

        assert os.path.exists(dist)
        contents = os.listdir(dist)
        assert len(contents) == 1

        self._build_path = os.path.join(dist, contents[0])

        # destination
        # use an evil recursive trick
        if destination:
            return self.package(destination=destination)

        return self._build_path

    def download(self, directory):
        """download a package and all its dependencies using pip"""
        if not os.path.exists(directory):
            os.makedirs(directory)
        assert os.path.isdir(directory)
        pip.main(['install', '--download', directory, self.src])

    def pypi(self, directory):
        """
        download packages for a pypi directory structure
        http://k0s.org/portfolio/pypi.html
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        assert os.path.isdir(directory)
        tempdir = tempfile.mkdtemp()
        try:
            self.download(tempdir)
            for package in os.listdir(tempdir):

                # full path
                src = os.path.join(tempdir, package)

                # make a package of the thing
                package = Package(src)

                # get destination dirname, filename
                dirname, filename = package.pypi_path()

                # make the directory if it doesn't exist
                subdir = os.path.join(directory, dirname)
                if not os.path.exists(subdir):
                    os.makedirs(subdir)
                assert os.path.isdir(subdir)

                # move the file
                self.package(destination=os.path.join(subdir, filename))
        finally:
            shutil.rmtree(tempdir)

    def pypi_path(self):
        """
        returns subpath 2-tuple appropriate for pypi path structure:
        http://k0s.org/portfolio/pypi.html
        """
        info = self.info()

        # determine the extension
        extension = self.extension()

        # get the filename destination
        name = info['Name']
        version = info['Version']
        filename = '%s-%s%s' % (name, version, extension)
        return name, filename
