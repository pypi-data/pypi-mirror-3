Release History
---------------


0.2.1 (2012-01-17)
~~~~~~~~~~~~~~~~~~

* Add MANIFEST.in so PyPI package contains all relevant files


0.2 (2012-01-04)
~~~~~~~~~~~~~~~~

* Issue #6: Added a ``min_depth`` option to ``filtered_walk`` and a new
  ``min_depth`` filter function to make it easier to produce a list of full
  subdirectory paths
* Issue #5: Renamed path iteration convenience APIs:
   * ``iter_paths`` -> ``all_paths``
   * ``iter_dir_paths`` -> ``dir_paths``
   * ``iter_file_paths`` -> ``file_paths``
* Moved version number to a VERSION.txt file (read by both docs and setup.py)
* Added NEWS.rst (and incorporated into documentation)


0.1 (2011-11-13)
~~~~~~~~~~~~~~~~

* Initial release
