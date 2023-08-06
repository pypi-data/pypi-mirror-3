# -*- coding: utf-8 -*-

import argparse
import sys

import pytest

from littlehttpserver.LittleHTTPServer import parse_argument

DEFAULT_PARSER_ARGS = {
    "doc_dirs": [], "index_dir": ".", "port": 8000, "protocol": "HTTP/1.0",
    "server_type": "process", "verbose": False
}

class ExpectedArgs(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.mark.parametrize(("argv", "expected"), [
    (["py"], {}),
    (["py", "-p", "8080"], {"port": 8080}),
    (["py", "--port", "8080"], {"port": 8080}),
    (["py", "-p", "8080", "-v"], {"port": 8080, "verbose": True}),
    (["py", "-d", "dir1", "-d", "dir2"],
        {"index_dir": None, "doc_dirs": ["dir1", "dir2"]}),
    (["py", "-i", "index", "-d", "dir1", "-d", "dir2"],
        {"index_dir": "index", "doc_dirs": ["dir1", "dir2"]}),
])
def test_parse_argument(argv, expected):
    sys.argv = argv
    expected_args = DEFAULT_PARSER_ARGS.copy()
    expected_args.update(**expected)
    assert parse_argument() == ExpectedArgs(**expected_args)

@pytest.mark.parametrize(("argv", "parents", "expected"), [
    (["py"], None, {}),
    (["py", "-p", "8080"], {"extra": "a"}, {"port": 8080, "extra": "a"}),
    (["py", "-p", "8080", "--extra", "b"], {"extra": "a"},
        {"port": 8080, "extra": "b"}),
    (["py", "--extra", "b", "--str", "c"], {"extra": "a", "str": "a"},
        {"extra": "b", "str": "c"}),
])
def test_parse_argument_with_parents(argv, parents, expected):
    def get_parent_parsers(parents):
        parser = argparse.ArgumentParser(add_help=False)
        parser.set_defaults(**parents)
        for key in parents.keys():
            parser.add_argument("--{0}".format(key), dest="{0}".format(key))
        return [parser]

    sys.argv = argv
    expected_args = DEFAULT_PARSER_ARGS.copy()
    expected_args.update(**expected)

    parent_parsers = get_parent_parsers(parents) if parents else []
    assert parse_argument(parent_parsers) == ExpectedArgs(**expected_args)
