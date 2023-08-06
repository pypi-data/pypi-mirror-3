# -*- coding: utf-8 -*-

import logging
import re
import tempfile
import os
from os.path import abspath, basename, isdir, join as pathjoin

_RE_DOCS_BUILD_DIR = re.compile(r"""
    (docs?/)?(en/|ja/)?(_?build/)?(sphinx/)?(html/?)?
""", re.U | re.X)

def get_package_name(path):
    """
    >>> get_package_name("/path/to/package-1.0/build/sphinx/html")
    'package-1.0'
    >>> get_package_name("/path/to/docs/package-1.0/build/html")
    'package-1.0'
    >>> get_package_name("/path/to/package-1.0/docs/build/html")
    'package-1.0'
    >>> get_package_name("/path/to/package-1.0/docs/_build/html")
    'package-1.0'
    >>> get_package_name("/path/to/package-1.0/docs/")
    'package-1.0'
    >>> get_package_name("/path/to/package/doc/_build/html")
    'package'
    >>> get_package_name("/path/to/package/doc/ja/_build/html")
    'package'
    >>> get_package_name("/path/to/package-doc-ja/build/html")  # FIXME
    'package-doc-ja'
    """
    subdir_stripped = re.sub(_RE_DOCS_BUILD_DIR, "", path).rstrip("/")
    return basename(subdir_stripped)

def make_symlink_to_dir(src, dst):
    abs_path = abspath(src)
    logging.debug("Absolute path: {0}".format(abs_path))
    if isdir(abs_path):
        os.symlink(abs_path, dst)
    else:
        logging.warning("{0} is not directory".format(abs_path))

def get_document_rootdir(doc_dirs):
    doc_root = tempfile.mkdtemp(prefix="LittleHTTPServer_")
    logging.debug("Doc Root: {0}".format(doc_root))
    for dir_ in doc_dirs:
        abs_path = abspath(dir_)
        pkg_name = get_package_name(abs_path)
        logging.debug("Package name: {0}".format(pkg_name))
        make_symlink_to_dir(abs_path, pathjoin(doc_root, pkg_name))
    return doc_root

def add_index_dir(doc_root, index_dir):
    abs_path = abspath(index_dir)
    make_symlink_to_dir(abs_path, pathjoin(doc_root, basename(abs_path)))
