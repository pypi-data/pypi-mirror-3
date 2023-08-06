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
    ("/path/to/package/build/sphinx/html", "package"),
    ("/path/to/package/build/sphinx/html/", "package"),
    ("/path/to/docs/package/build/html", "package"),
    ("/path/to/package/docs/", "_path_to_package_docs_"),
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
