# -*- coding: utf-8 -*-

import logging
import re
import tempfile
import os
from os.path import abspath, basename, isdir, join as pathjoin

_RE_PACKAGE_NAME = re.compile(r"""
    .*/(?P<pkg_name>.*?)/build/(sphinx/){0,1}html/?
""", re.U | re.X)

def get_package_name(path):
    """ FIXME: should be added more pattern
    >>> get_package_name("/path/to/package/build/sphinx/html")
    'package'
    >>> get_package_name("/path/to/docs/package/build/html")
    'package'
    >>> get_package_name("/path/to/package/docs/")
    '_path_to_package_docs_'
    """
    match = re.search(_RE_PACKAGE_NAME, path)
    if match:
        return match.groupdict().get("pkg_name")
    else:
        return path.replace("/", "_")

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
