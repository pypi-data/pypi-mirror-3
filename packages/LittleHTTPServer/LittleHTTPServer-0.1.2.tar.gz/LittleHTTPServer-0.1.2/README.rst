
What is it?
===========

``LittleHTTPServer`` is intended to extend SimpleHTTPServer a little bit more.

Requirements
------------

* Python 2.6 or 3.x and later

Features
--------

* Provide an arbitrary directory not only current directory
* Provide some Sphinx document directories
* Provide selectable SocketServer type, Threading or Forking

Setup
=====

::

   $ easy_install LittleHTTPServer

Quick Start
===========

::

  $ littlehttpserver -v -i path/to/top

Show the link to "top" directory via "http://localhost:8000/".

Another example.

::

  $ littlehttpserver -v -d path/to/pkg1/build/html
                        -d path/to/pkg2/build/sphinx/html

Show the link to "pkg1" and "pkg2" optimized Sphinx documents.

::

  $ littlehttpserver -h
  usage: littlehttpserver [-h] [-d DOCUMENT_DIR] [-i INDEX_DIRECTORY]
                          [-p PORT_NUMBER] [-v] [--protocol PROTOCOL]
                          [--servertype {process,thread}] [--version]
  
  optional arguments:
    -h, --help            show this help message and exit
    -d DOCUMENT_DIR, --dir DOCUMENT_DIR
                          set some document directories
    -i INDEX_DIRECTORY, --indexdir INDEX_DIRECTORY
                          set arbitrary top directory
    -p PORT_NUMBER, --port PORT_NUMBER
                          set server port number
    -v, --verbose         set verbose mode
    --protocol PROTOCOL   set protocol
    --servertype {process,thread}
                          set server type
    --version             show program version
