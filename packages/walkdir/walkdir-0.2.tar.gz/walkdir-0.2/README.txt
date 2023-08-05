walkdir is a simple set of iterator tools intended to make it
easy to manipulate and filter the output of os.walk() in a way
that is also easily applicable to any source iterator that
produces data in the same format.

It offers tools such as:

  - glob-style filtering for file and directory names
  - depth limiting for directory recursion
  - flattening of output into simple sequences of path names
  - detection of symlink loops when following symlinks