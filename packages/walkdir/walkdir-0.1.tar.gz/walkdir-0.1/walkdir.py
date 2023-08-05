"""walkdir - iterative tools for working with os.walk() and similar interfaces
"""
import fnmatch
import os.path
import sys

# Should be compatible with 2.7 and 3.2+
try:
    _str_base = basestring
except NameError:
    _str_base = str

# Filtering for inclusion

def _make_include_filter(patterns):
    """Create a filtering function from a collection of inclusion patterns"""
    # Trivial case: exclude everything
    if not patterns:
        def _filter(names):
            return names[0:0]
        return _filter
    # Use fnmatch.filter if it's applicable
    if len(patterns) == 1:
        def _filter(names):
            return fnmatch.filter(names, patterns[0])
        return _filter
    # Handle the general case for inclusion
    def _should_include(name):
        return any(fnmatch.fnmatch(name, pattern)
                        for pattern in patterns)
    def _filter(names):
        for name in names:
            if _should_include(name):
                yield name
    return _filter
    
def include_dirs(walk_iter, *include_filters):
    """Use :func:`fnmatch.fnmatch` patterns to select directories of interest
    
       Inclusion filters are passed directly as arguments
    """
    filter_subdirs = _make_include_filter(include_filters)
    for dirpath, subdirs, files in walk_iter:
        subdirs[:] = filter_subdirs(subdirs)
        yield dirpath, subdirs, files

def include_files(walk_iter, *include_filters):
    """Use :func:`fnmatch.fnmatch` patterns to select files of interest
    
       Inclusion filters are passed directly as arguments
    """
    filter_files = _make_include_filter(include_filters)
    for dirpath, subdirs, files in walk_iter:
        files[:] = filter_files(files)
        yield dirpath, subdirs, files

# Filtering for exclusion

def _make_exclude_filter(patterns):
    """Create a filtering function from a collection of exclusion patterns"""
    # Trivial case: include everything
    if not patterns:
        def _filter(names):
            return names
        return _filter
    # Handle the general case for exclusion
    def _should_exclude(name):
        return any(fnmatch.fnmatch(name, pattern)
                        for pattern in patterns)
    def _filter(names):
        for name in names:
            if not _should_exclude(name):
                yield name
    return _filter

def exclude_dirs(walk_iter, *exclude_filters):
    """Use :func:`fnmatch.fnmatch` patterns to skip irrelevant directories
    
       Exclusion filters are passed directly as arguments
    """
    filter_subdirs = _make_exclude_filter(exclude_filters)
    for dirpath, subdirs, files in walk_iter:
        subdirs[:] = filter_subdirs(subdirs)
        yield dirpath, subdirs, files

def exclude_files(walk_iter, *exclude_filters):
    """Use :func:`fnmatch.fnmatch` patterns to skip irrelevant files
    
       Exclusion filters are passed directly as arguments
    """
    filter_files = _make_exclude_filter(exclude_filters)
    for dirpath, subdirs, files in walk_iter:
        files[:] = filter_files(files)
        yield dirpath, subdirs, files


# Depth limiting

def limit_depth(walk_iter, depth):
    """Limit the depth of recursion into subdirectories.
    
       A depth of 0 limits the walk to the top level directory
    """
    if depth < 0:
        msg = "Depth limit greater than 0 ({!r} provided)"
        raise ValueError(msg.format(depth))
    sep=os.sep
    for top, subdirs, files in walk_iter:
        yield top, subdirs, files
        initial_depth = top.count(sep)
        if depth == 0:
            subdirs[:] = []
        break
    for dirpath, subdirs, files in walk_iter:
        yield dirpath, subdirs, files
        current_depth = dirpath.count(sep) - initial_depth
        if current_depth >= depth:
            subdirs[:] = []

# Symlink loop handling

def handle_symlink_loops(walk_iter, onloop=None):
    """Handle symlink loops when following symlinks during a walk
    
       By default, prints a warning and then skips processing
       the directory a second time. 
       
       This can be overridden by providing the `onloop` callback, which
       accepts the offending symlink as a parameter. Returning a true value
       from this callback will mean that the directory is still processed,
       otherwise it will be skipped.
    """
    if onloop is None:
        def onloop(dirpath):
            msg = "Symlink {!r} refers to a parent directory, skipping\n"
            sys.stderr.write(msg.format(dirpath))
            sys.stderr.flush()
    sep=os.sep
    for top, subdirs, files in walk_iter:
        yield top, subdirs, files
        real_top = os.path.abspath(os.path.realpath(top))
        break
    for dirpath, subdirs, files in walk_iter:
        if os.path.islink(dirpath):
            # We just descended into a directory via a symbolic link
            # Check if we're referring to a directory that is
            # a parent of our nominal directory
            relative = os.path.relpath(dirpath, top)
            nominal_path = os.path.join(real_top, relative)
            real_path = os.path.abspath(os.path.realpath(dirpath))
            path_fragments = zip(nominal_path.split(sep), real_path.split(sep))
            for nominal, real in path_fragments:
                if nominal != real:
                    break
            else:
                if not onloop(dirpath):
                    subdirs[:] = []
                    continue
        yield dirpath, subdirs, files

# Convenience function that puts together an iterator pipeline

def filtered_walk(top, included_files=None, included_dirs=None,
                       excluded_files=None, excluded_dirs=None,
                       depth=None, followlinks=False):
    """This is a wrapper around ``os.walk()``, with these additional features:
        - *top* may be either a string (which will be passed to ``os.walk()``)
          or any iterable that produces ``path, subdirs, files`` triples
        - allows independent glob-style filters for filenames and subdirectories
        - allows a recursion depth limit to be specified
        - emits a message to stderr and skips the directory if a symlink loop
          is encountered when following links

       Filtered walks are always top down, as the subdirectory listings must
       be altered to provide a number of the above features.

       *include_files*, *include_dirs*, *exclude_files* and *exclude_dirs* are
       used to apply the relevant filtering steps to the walk.
       
       A *depth* of ``None`` (the default) disables depth limiting. Otherwise,
       *depth* must be at least zero and indicates how far to descend into the
       directory hierarchy. A depth of zero is useful to get separate filtered
       subdirectory and file listings for *top*.

       *followlinks* enables symbolic loop detection and is also passed to
       ``os.walk()`` when top is a string
    """
    if isinstance(top, str):
        walk_iter = os.walk(top, followlinks=followlinks)
    else:
        walk_iter = top
    # Depth filtering first, since it can cut great swathes from the tree
    if depth is not None:
        walk_iter = limit_depth(walk_iter, depth)
    # Next we do our path based filtering that can skip directories
    if included_dirs is not None:
        walk_iter = include_dirs(walk_iter, *included_dirs)
    if excluded_dirs is not None:
        walk_iter = exclude_dirs(walk_iter, *excluded_dirs)
    # And then we check the filesystem for symlink loops
    if followlinks:
        walk_iter = handle_symlink_loops(walk_iter)
    # Finally, apply the file filters that can't alter the shape of the tree
    if included_files is not None:
        walk_iter = include_files(walk_iter, *included_files)
    if excluded_files is not None:
        walk_iter = exclude_files(walk_iter, *excluded_files)
    for triple in walk_iter:
        yield triple


# Iterators that flatten the output into a series of paths

def iter_dir_paths(walk_iter):
    """Iterate over just the directory names visited by the underlying walk"""
    for dirpath, subdirs, files in walk_iter:
        yield dirpath

def iter_file_paths(walk_iter):
    """Iterate over the files in directories visited by the underlying walk"""
    for dirpath, subdirs, files in walk_iter:
        for fname in files:
            yield os.path.join(dirpath, fname)

def iter_paths(walk_iter):
    """Iterate over both files and directories visited by the underlying walk"""
    for dirpath, subdirs, files in walk_iter:
        yield dirpath
        for fname in files:
            yield os.path.join(dirpath, fname)
    