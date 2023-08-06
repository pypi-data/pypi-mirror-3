# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
from os.path import abspath, basename, isdir, islink, join as pathjoin

import pytest

from littlehttpserver.utils.env import (
    add_index_dir, get_document_rootdir, get_package_name,
    make_symlink_to_dir)

@pytest.mark.parametrize(("path", "expected"), [
    ("/path/to/package-1.0/build/sphinx/html", "package-1.0"),
    ("/path/to/package-1.1/build/sphinx/html/", "package-1.1"),
    ("/path/to/package-sub-1.2/build/sphinx/html/", "package-sub-1.2"),
    ("/path/to/package-sub-ext-1.3/build/sphinx/html", "package-sub-ext-1.3"),
    ("/path/to/doc/package-2.0.0/build/html", "package-2.0.0"),
    ("/path/to/docs/package-2.0.1/build/html", "package-2.0.1"),
    ("/path/to/docs/package-sub-2.0.2/build/html", "package-sub-2.0.2"),
    ("/path/to/package-3.0a/doc/build/html", "package-3.0a"),
    ("/path/to/package-3.1a/docs/build/html", "package-3.1a"),
    ("/path/to/doc/package_sub-4.0/build/html", "package_sub-4.0"),
    ("/path/to/docs/package_sub-4.1/build/html", "package_sub-4.1"),
    ("/path/to/package-2011.12/build/sphinx/html", "package-2011.12"),
    ("/path/to/package-2012.1.15/build/sphinx/html", "package-2012.1.15"),
    ("/path/to/package_sub-2012.2/build/sphinx/html", "package_sub-2012.2"),
    ("/path/to/package/docs/", "_path_to_package_docs_"),
    ("/path/to/package-1.0/docs/", "_path_to_package-1.0_docs_"),
    ("/path/to/package-sub-1.1/docs/", "_path_to_package-sub-1.1_docs_"),
])
def test_get_package_name(path, expected):
    assert expected == get_package_name(path)

class TestMakingSymlink(object):

    def setup_method(self, method):
        self.test_root = tempfile.mkdtemp(prefix="TestMakingSymlink_")

    @pytest.mark.parametrize(("src", "dst", "expected"), [
        (".", "current", True),
        ("..", "parrent", True),
        ("detarame", "detarame", False),
    ])
    def test_make_symlink_to_dir(self, src, dst, expected):
        dst = pathjoin(self.test_root, dst)
        make_symlink_to_dir(src, dst)
        if islink(dst):
            actual = abspath(src) == os.readlink(dst)
        else:
            actual = False
        assert expected == actual

    @pytest.mark.parametrize("doc_dirs", [
        [".", ".."],
    ])
    def test_get_document_rootdir(self, doc_dirs):
        doc_root = None
        try:
            doc_root = get_document_rootdir(doc_dirs)
            assert isdir(doc_root)
            assert len(doc_dirs) == len(os.listdir(doc_root))
        finally:
            if doc_root:
                shutil.rmtree(doc_root, ignore_errors=True)

    def test_add_index_dir(self):
        base_name = basename(abspath("."))
        add_index_dir(self.test_root, ".")
        assert islink(pathjoin(self.test_root, base_name))

    def teardown_method(self, method):
        shutil.rmtree(self.test_root)
