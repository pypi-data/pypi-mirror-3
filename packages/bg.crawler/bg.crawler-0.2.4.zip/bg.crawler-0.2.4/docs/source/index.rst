Introduction
============

``bg.crawler`` is a command-line frontend for feeding a tree of files (a
directory) into a Solr for indexing. 

Requirements
============

* Python 2.6 or Python 2.7 (no support for Python 3)
* ``curl`` 

Installation
============

* use ``easy_install bg.crawler`` - this should install
  a script ``solr-crawler`` inside the ``bin`` folder
  of your Python installation. You are strongly encouraged
  to use ``virtualenv`` for creating a virtualized Python environment.  

Usage
=====

Command line options::

    blackmoon:~/src/bg.crawler> bin/solr-crawler --help
    usage: solr-crawler [-h] [--solr-url SOLR_URL] [--max-depth MAX_DEPTH]
                        [--commit-after COMMIT_AFTER] [--tag TAG] [--clear-all]
                        [--clear-tag SOLR_CLEAR_TAG] [--verbose] [--no-type-check]
                        <directory>

    Commandline parser

    positional arguments:
      <directory>           Directory to be crawled

    optional arguments:
      -h, --help            show this help message and exit
      --solr-url SOLR_URL   SOLR server URL
      --max-depth MAX_DEPTH
                            maximum folder depth
      --commit-after COMMIT_AFTER
                            Solr commit every COMMIT_AFTER documents
      --tag TAG             Solr import tag
      --clear-all           Clear the Solr indexes before crawling
      --clear-tag SOLR_CLEAR_TAG
                            Remove all items from Solr indexed tagged with the
                            given tag
      --verbose             Verbose logging
      --no-type-check       Apply extension filter while crawling


* ``--solr-url`` defines the URL of the SOLR server

* ``--max-depth`` limits the crawler to a given folder depth

* ``--tag`` will tag the imported document(s) with a string
  (this may be useful importing different document sources
  into Solr while supporting the option to filter by tag
  at query time)

* ``--clear-all`` clear the complete Solr index before running
  the import

* ``--clear-tag`` remove all documents with the given tag before
  running the import

* ``--verbose`` enable extensive logging

* ``--no-type-check`` if set: do not apply any type check filtering
  but instead pass all file types to Solr

Internals
=========

* uses the ``python-magic`` module to determine the mimetype of
  files to be imported
* currently deals with HTML and plain text files
* HTML files are currently parsed internally and converted to 
  plain text

Sourcecode
==========

https://github.com/zopyx/bg.crawler


Bug tracker
===========

https://github.com/zopyx/bg.crawler/issues

Solr setup
==========

You can use the buildout configuration from

https://raw.github.com/zopyx/bg.crawler/master/solr-3.4.cfg

as an example how to setup a Solr instance for using
``bg.crawler``.

It is important that the following field type definition is
available within your Solr instance::

    index =
        name:text             type:text    stored:true
        name:title            type:text    stored:true
        name:created          type:date    stored:true required:true
        name:modified         type:date    stored:true 
        name:filesize         type:integer stored:true 
        name:mimetype         type:string  stored:true
        name:id               type:string  stored:true required:true
        name:tag              type:string  stored:true

After running ``buildout`` you can start the Solr instance using::

    bin/solr-instance fg|start

Licence
=======

``bg.crawler`` is published under the GNU Public Licence V2 (GPL 2)

Credits
=======

``bg.crawler`` is sponsored by BG Phoenics

Author
======

| ZOPYX Ltd.
| Charlottenstr. 37/1
| D-72070 Tuebingen
| Germany
| info@zopyx.com
| www.zopyx.com

