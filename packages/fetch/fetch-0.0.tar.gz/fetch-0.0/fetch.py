#!/usr/bin/env python

"""
fetch stuff from the interwebs
"""

import optparse
import os
import shutil
import sys
import tempfile

__all__ = ['Fetcher', 'Fetch', 'main']

def which(executable, path=os.environ['PATH']):
    """python equivalent of which; should really be in the stdlib"""
    dirs = path.split(os.pathsep)
    for dir in dirs:
        if os.path.isfile(os.path.join(dir, executable)):
            return os.path.join(dir, executable)

def copytree(src, dst):
    """
    replacement for shutil.copytree because of this nonsense from help(shutil.copytree):
      "The destination directory must not already exist."
    """

    assert os.path.exists(src), "'%s' does not exist" % src

    # if its a file, just copy it
    if os.path.isfile(src):
        shutil.copy2(src, dst)
        return

    # otherwise a directory
    assert os.path.isdir(src)
    if os.path.exists(dst):
        assert os.path.isdir(dst), "%s is a file, %s is a directory" % (src, dst)
    else:
        os.makedirs(dst)

    src = os.path.realpath(src)
    for dirpath, dirnames, filenames in os.walk(src):
        for d in dirnames:
            path = os.path.join(dirpath, d)
            _dst = os.path.join(dst, os.path.relpath(path, src)) # XXX depends on python 2.5 relpath
            if os.path.exists(_dst):
                assert os.path.isdir(_dst), "%s is a file, %s is a directory" % (src, dst)
            else:
                os.makedirs(_dst)
        for f in filenames:
            path = os.path.join(dirpath, f)
            _dst = os.path.join(dst, os.path.relpath(path, src)) # XXX depends on python 2.5 relpath
            shutil.copy2(path, _dst)

class Fetcher(object):
    """abstract base class for resource fetchers"""

    @classmethod
    def match(cls, _type):
        return _type == cls.type

    def __init__(self, url):
        self.subpath = None
        if '#' in url:
            url, self.subpath = url.rsplit('#')
            if self.subpath:
                self.subpath = self.subpath.split('/')
        self.url = url

    def __call__(self, dest):
        raise NotImplementedError("Should be called by implementing class")

    @classmethod
    def doc(cls):
        """return docstring for the instance"""
        retval = getattr(cls, '__doc__', '').strip()
        return ' '.join(retval.split())

### standard dispatchers - always available

import tarfile
import urllib2
from StringIO import StringIO

class FileFetcher(Fetcher):
    """fetch a single file"""
    # Note: subpath for single files is ignored

    type = 'file'

    @classmethod
    def download(cls, url):
        return urllib2.urlopen(url).read()

    def __call__(self, dest):

        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        if os.path.isdir(dest):
            filename = self.url.rsplit('/', 1)[-1]
            dest = os.path.join(dest, filename)
        f = file(dest, 'w')
        f.write(self.download(self.url))
        f.close()


class TarballFetcher(FileFetcher):
    """fetch and extract a tarball"""

    type = 'tar'

    def __call__(self, dest):
        if os.path.exists(dest):
            assert os.path.isdir(dest), "Destination must be a directory"
        else:
            os.makedirs(dest)
        buffer = StringIO()
        buffer.write(self.download(self.url))
        buffer.seek(0)
        tf = tarfile.open(mode='r', fileobj=buffer)
        members = tf.getmembers()
        if self.subpath:

            # build list of files to extract
            _members = []

            toppath = None
            for member in members:
                split = member.name.split(os.path.sep)
                if toppath:
                    # ensure that for subpaths that only one top level directory exists
                    # XXX needed?
                    assert toppath == split[0], "Multiple top-level archives found"
                else:
                    toppath = split[0]
                if split and split[1:len(self.subpath)+1] == self.subpath:
                    member.name = os.path.sep.join(split[1:])
                    _members.append(member)

            members = _members

        for member in members:
            tf.extract(member, dest)

fetchers = [FileFetcher, TarballFetcher]

### VCS fetchers

import subprocess
try:
    from subprocess import check_call as call
except ImportErorr:
    raise # we need check_call, kinda

class VCSFetcher(Fetcher):

    command = None # name of the VCS command (currently unused)

    def __init__(self, url, export=True):
        """
        - export : whether to strip the versioning information
        """
        Fetcher.__init__(self, url)
        self._export = export
        self.prog = self.type # name of app program
        self.vcs_dir = '.' + self.type # subdirectory for version control

    def call(*args, **kwargs):
        assert command is not None, "Abstract base class"
        call([self.command] + list(args), **kwargs)

    def __call__(self, dest):

        if self.subpath or self._export:
            # can only export with a subpath
            self.export(dest)
            return

        if os.path.exists(dest):
            assert os.path.isdir(dest)
        else:
            self.clone(dest)

    def export(self, dest):
        """
        export a clone of the directory
        """
        dest = os.path.abspath(dest)
        tmpdir = tempfile.mkdtemp()
        self.clone(tmpdir)
        if self.vcs_dir:
            shutil.rmtree(os.path.join(tmpdir, self.vcs_dir))
        path = tmpdir
        if self.subpath:
            path = os.path.join(*([tmpdir] + self.subpath))
            assert os.path.exists(path), "subpath %s of %s not found" % (os.path.sep.join(self.subpath), self.url)
        if os.path.isdir(path):
            if os.path.exists(dest):
                assert os.path.isdir(dest), "source is a directory; destination is a file"
            else:
                os.makedirs(dest)
            copytree(path, dest)
        else:
            if not os.path.exists(dest):
                directory, filename = os.path.split(dest)
                if os.path.exists(directory):
                    assert os.path.isdir(directory), "%s is not a directory" % directory
                else:
                    os.makedirs(directory)
            shutil.copy(path, dest)
        shutil.rmtree(tmpdir)

    def clone(self, dest):
        """
        clones into a directory
        """
        raise NotImplementedError("Abstract base class")

    def update(self, dest):
        """
        updates a checkout
        """
        raise NotImplementedError("Abstract base class")

    def versioned(self, directory):
        return os.path.exists(os.path.join(directory, self.vcs_dir))


if which('hg'):

    class HgFetcher(VCSFetcher):
        """checkout a mercurial repository"""
        type = 'hg'

        def __init__(self, url, export=True):
            VCSFetcher.__init__(self, url, export=export)
            self.hg = which('hg')
            assert self.hg, "'hg' command not found"

        def clone(self, dest):
            if os.path.exists(dest):
                assert os.path.isdir(dest)
            call([self.hg, 'clone', self.url, dest])

        def update(self, dest):
            assert os.path.versioned(dest)
            assert os.path.exists(dest)
            call([self.hg, 'pull', self.url], cwd=dest)
            call([self.hg, 'update', '-C'], cwd=dest)


    fetchers.append(HgFetcher)

if which('git'):

    class GitFetcher(VCSFetcher):
        """checkout a git repository"""
        type = 'git'

        def __init__(self, url, export=True):
            VCSFetcher.__init__(self, url, export=export)
            self.git = which('git')
            assert self.git, "'git' command not found"

        def update(self, dest):
            assert os.path.isdir(dest)
            assert os.path.versioned(dest)
            call([self.git, 'pull', self.url], cwd=dest)
            call([self.git, 'update'], cwd=dest)

        def clone(self, dest):
            if not os.path.exists(dest):
                os.makedirs(dest)
            call([self.git, 'clone', self.url, dest])

    fetchers.append(GitFetcher)

__all__ += [i.__name__ for i in fetchers]

class Fetch(object):

    def __init__(self, fetchers=fetchers[:], relative_to=None, strict=True, clobber=True):
        self.fetchers = fetchers
        self.relative_to = relative_to
        self.strict = strict
        self._clobber = clobber

    def fetcher(self, _type):
        """find the fetcher for the appropriate type"""
        for fetcher in fetchers:
            if fetcher.match(_type):
                return fetcher

    def __call__(self, url, destination, type, **options):
        fetcher = self.fetcher(type)
        assert fetcher is not None, "No fetcher found for type '%s'" % type
        fetcher = fetcher(url, **options)
        fetcher(destination)

    def clobber(self, dest):
        """clobbers if self._clobber is set"""
        if self._clobber and os.path.exists(dest):
            if os.path.isfile(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)

    def fetch(self, *items):

        if self.strict:
            # ensure all the required fetchers are available
            types = set([i['type'] for i in items])
            assert not [i for i in types
                        if not [True for fetcher in fetchers
                                if fetcher.match(i)]]

        for item in items:

            # fix up relative paths
            dest = item['dest']
            if not os.path.isabs(dest):
                relative_to = self.relative_to
                if not relative_to:
                    if isinstance(item['manifest'], basestring):
                        relative_to = os.path.dirname(os.path.abspath(item['manifest']))
                    else:
                        relative_to = os.getcwd()
                dest = os.path.normpath(os.path.join(relative_to, dest))

            # fetch the items
            self(item['url'], destination=dest, type=item['type'], **item['options'])


format_string = "[URL] [destination] [type] <options>"
def read_manifests(*manifests):
    """
    read some manifests and return the items

    Format:
    %s
    """ % format_string

    retval = []

    for manifest in manifests:
        if isinstance(manifest, basestring):
            assert os.path.exists(manifest), "manifest '%s' not found" % manifest
            f = file(manifest)
        else:
            f = manifest

        for line in f.readlines():
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            line = line.split()
            if len(line) not in (3,4):
                raise Exception("Format should be: %s; line %s" % (format_string, line))
            options = {}
            if len(line) == 4:
                option_string = line.pop().rstrip(',')
                try:
                    options = dict([[j.strip() for j in i.split('=', 1)]
                                    for i in option_string.split(',')])
                except:
                    raise Exception("Options format should be: key=value,key2=value2,...; got %s" % option_string)

            url, dest, _type = line
            retval.append(dict(url=url, dest=dest, type=_type, options=options, manifest=manifest))
    return retval

def main(args=sys.argv[1:]):

    # parse command line options
    usage = '%prog [options] manifest [manifest] [...]'

    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        def format_description(self, description):
            if description:
                return description + '\n'
            else:
                return ''

    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    parser.add_option('-o', '--output',
                      help="output relative to this location vs. the manifest location")
    parser.add_option('-d', '--dest', # XXX unused
                      action='append',
                      help="output only these destinations")
    parser.add_option('-s', '--strict',
                      action='store_true', default=False,
                      help="fail on error")
    parser.add_option('--list-fetchers', dest='list_fetchers',
                      action='store_true', default=False,
                      help='list available fetchers and exit')
    options, args = parser.parse_args(args)

    if options.list_fetchers:
        types = set()
        for fetcher in fetchers:
            if fetcher.type in types:
                continue # occluded, should probably display separately
            print '%s : %s' % (fetcher.type, fetcher.doc())
            types.add(fetcher.type)
        parser.exit()

    if not args:
        # TODO: could read from stdin
        parser.print_help()
        parser.exit()

    # sanity check
    assert not [i for i in args if not os.path.exists(i)]

    items = read_manifests(*args)
    fetch = Fetch(fetchers, relative_to=options.output, strict=options.strict)

    # download the files
    fetch.fetch(*items)

if __name__ == '__main__':
    main()
