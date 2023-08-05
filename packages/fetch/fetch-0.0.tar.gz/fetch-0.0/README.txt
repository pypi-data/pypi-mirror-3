fetch
=====

fetch stuff from the interwebs

`fetch.py <http://k0s.org/mozilla/hg/fetch/raw-file/tip/fetch.py>`_ is
a single-file python module bundled as a
`package <http://k0s.org/mozilla/hg/fetch/>`_ for easy installation
and python importing.  The purpose of fetch is to mirror remote
resources (URLs) to a local filesystem in order to synchronize and
update dependencies that are desired to be mirrored in this way.


Format
------

``fetch`` fetches from a manifest of the format::

 [URL] [Destination] [Type]

A URL can contain a hash tag (e.g. http://example.com/foo#bar/fleem)
which is used to extract the subdirectories from a multi-directory
resource.

The ``Type`` of the resource is used to dispatch to the included
Fetchers that take care of fetching the object.

Manifests are used so that a number of resources may be fetched from a
particular ``fetch`` run.


Example
-------

After you checkout the `repository <http://k0s.org/mozilla/hg/fetch>`_
and run ``python setup.py develop``, you should be able to run
``fetch`` on the example manifest::

 fetch example.txt

This will create a ``tmp`` directory relative to the manifest and pull
down several resources to it.


Fetchers
--------

``fetch`` includes several objects for fetching resources::

 file : fetch a single file
 tar : fetch and extract a tarball
 hg : checkout a mercurial repository
 git : checkout a git repository

The ``file`` fetcher cannot have a hash tag subpath since it is a single
resource.

Though ``fetch`` has a set of fetchers included, you can pass an
arbitrary list into ``fetch.Fetch``'s constructor.


Version Control
---------------

The ``hg`` and the ``git`` fetchers fetch from version control systems and
have additional options.  The only current option to the constructor
is ``export``, which is by default True.  If ``export`` is True, then
the repository will be exported into a non-versioned structure.  If a
subpath is specified with a ``#`` in the URL, the repository will also
be exported.


TODO
----

 * use `manifestparser <https://github.com/mozilla/mozbase/blob/master/manifestdestiny/manifestparser.py>`_
   ``.ini`` files versus another manifest
   format: when I started work on ``fetch``, I thought a
   domain-specific manifest would be a big win.  But, now, maybe a
   ``.ini`` type manifest looks about the same, and is something that
   is already used.  The switch internally wouldn't be that bad, but
   if ``fetch.py`` is used as a single file, it cannot have
   "traditional" python dependencies. Since ``manifestparser.py`` is
   also a single file, and ``fetch`` is only usable with internet
   access anyway, maybe the
   `require <http://k0s.org/hg/config/file/tip/python/require.py>`_
   pattern could be used for this purpose

 * clobber: generally, you will want the existing resource to be
   clobbered, avoiding renames regarding upstream dependencies

 * outputting only subpaths: often, you will not to fetch from the
   whole manifest, only from certain subpaths of the manifest.  You
   should be able to output a subset of what is to be mirrored based
   on destination subpaths.  The CLI option ``--dest`` is intended for
   this purpose but currently unused.

 * fetcher options: currently ``read_manifests`` reads an unused
   column into ``options`` when present in the form of a string like
   ``foo=one,bar=two`` into a dict like
   ``{'foo': 'one', 'bar': 'two'}``.  This hasn't been needed yet and
   is unused.  If we want to have resource-specific options, we should
   use this and make it work.  Otherwise it can be deleted.

 * python package fetcher: often you will want to fetch a python
   package as a resource.  This would essentially fetch the object
   (using another fetcher) and take the (untarred) result of
   ``python setup.py sdist`` as a resource.  This will strip out files
   that aren't part of the python package. Unknowns include how to
   specify the sub-fetcher. You could also include other
   domain-specific fetchers as needed.

 * note python 2.5+ specifics: ``fetch`` currently uses at least
   ``os.path.relpath`` from python 2.5 and perhaps other 2.5+isms as
   well. These should at least be documented and checked for if not
   obviated. One such reimplementation is at
   https://github.com/mozilla/mozbase/blob/master/manifestdestiny/manifestparser.py#L66


Unsolved Problems
-----------------

A common story for ``fetch`` is mirroring files into a VCS repository
because the remote resources are needed as part of the repository and
there is no better way to retrieve and/or update them.  However, what
do you do if these remote resources are altered?  In an ideal
ecosystem, the fixes would be automatically triaged and triggered for
upstream inclusion, or the diffs from the upstream are kept in local
modifications (although vendor branches, etc, are more suitable for
the latter class of problems, and in general discouraged when a less
intrusive system of consuming upstream dependencies are available).

----

Jeff Hammel
http://k0s.org/mozilla/hg/fetch
