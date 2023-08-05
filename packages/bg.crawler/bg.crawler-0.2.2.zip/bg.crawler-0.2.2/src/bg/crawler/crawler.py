################################################################
# bg.crawler
# (C) 2011, ZOPYX Ltd.  - written for BG Phoenics
################################################################

import time
import os
import sys
import magic
import sunburnt
import argparse
import lxml.html
import httplib
import urllib
import urlparse
import hashlib
import base64
import subprocess
from logger import LOG
from datetime import datetime

EXTENSIONS = (
    '.html',
    '.htm',
    '.txt', 
    '.pdf',
    '.doc', 
    '.docx',
)

def binary_add(solr_connection, data, fullname):
    """ Manually inject binary data through a HTTP
        Post request since sunburnt does not seem to expose
        an API for posting binary data.
    """

    params = {'fmap.content' : 'text',
              'literal.id' : data['id'],
              'literal.modified' : data['modified'],
              'literal.tag' : data['tag'],
              'literal.mimetype' : data['mimetype'],
              'literal.relpath' : data['relpath'],
              'literal.filesize' : data['filesize'],
              'literal.modified' : data['modified'],
              'literal.created' : data['created'],
             }

    curl_cmd = 'curl "%sextract?%s"' % (solr_connection.conn.update_url, urllib.urlencode(params))
    curl_cmd += ' -s -o /dev/null -F "myfile=@%s"' % fullname
    LOG.debug(curl_cmd)
    status = subprocess.call(curl_cmd, shell=True)
    LOG.debug('Curl exit status: %d' % status)

def crawl(args):

    LOG.info('Started SOLR import')
    LOG.info(args)

    ts = time.time()
    solr_connection = sunburnt.SolrInterface(args.solr_url)
    mime = magic.Magic(mime=True)

    if args.solr_clear:
        LOG.info('Clearing Solr indexes')
        solr_connection.delete_all()
        solr_connection.commit()

    if args.solr_clear_tag:
        LOG.info('Removing documents from index tagged with "%s"' % args.solr_clear_tag)
        solr_connection.delete(queries=solr_connection.Q(tag=args.solr_clear_tag))
        solr_connection.commit()

    count = 0
    batch_num = 0
    contents = list()
    root_directory = os.path.abspath(args.directory)
    for dirpath, dirname, filenames in os.walk(root_directory):
        for filename in filenames:

            depth = dirpath.replace(args.directory, '').count('/')
            fullname = os.path.join(dirpath, filename)
            relpath = fullname.replace(root_directory, '').lstrip('/')

            # check max traversal depth parameter
            if args.max_depth and depth > args.max_depth:
                LOG.debug('Skipping %s (depth check)' % fullname)
                continue

            # don't deal with stuff other than files
            if not os.path.isfile(fullname):
                LOG.debug('Skipping %s (not a file)' % fullname)
                continue

            # extension checking
            basename, ext = os.path.splitext(filename)
            ext = ext.lower()
            if not args.no_type_check and not ext in EXTENSIONS:
                LOG.debug('Skipping %s (type check)' % fullname)
                continue

            if args.verbose:
                LOG.info('Processing: %s' % fullname)
            
            text = file(fullname, 'rb').read()
            title = ''
            body = ''
            mimetype = mime.from_file(fullname)

            created = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            modified = datetime.fromtimestamp(os.path.getmtime(fullname)).strftime('%Y-%m-%dT%H:%M:%SZ')
            filesize = os.path.getsize(fullname)

            textish_content = mimetype.startswith('text/')

            if mimetype in ('text/html',):
                root = lxml.html.fromstring(text)

                nodes = root.xpath('//body')
                if nodes:
                    text = nodes[0].text_content()

                nodes = root.xpath('//title')
                if nodes:
                    title = nodes[0].text_content()
            elif mimetype.startswith('text/'):
                try:
                    text = unicode(text, 'utf-8')
                except UnicodeError:
                    text = unicode(text, 'utf-8', 'ignore')

            count += 1 

            # Some marshalling is need in order to preserve
            # encoded strings (e.g. for filenames containing non-ascii
            # characters. The 'id' is generated from the SHA1 hash
            # of the full filename.

            id = hashlib.sha1(fullname).hexdigest()
            data = dict(id=id,
                        text=text, 
                        title=title,
                        tag=args.tag,
                        mimetype=mimetype, 
                        relpath=base64.encodestring(relpath),
                        fullpath=base64.encodestring(fullname),
                        filesize=filesize,
                        modified=modified,
                        created=created
                        )

            # add documents (for non-batch mode)
            if not args.batch_size:
                try:
                    if textish_content:
                        solr_connection.add(data)
                    else:
                        data['text'] = ''
                        solr_connection.add(data)
                        binary_add(solr_connection, data, fullname)
                except Exception, e:
                    LOG.error('Content could not be added', exc_info=True)

            else:
                # batched add_many operation
                contents.append(data)
                if batch_num > args.batch_size:
                    try:
                        if textish_content:
                            solr_connection.add(data)
                        else:
                            data['text'] = ''
                            solr_connection.add(data)
                            binary_add(solr_connection, data, fullname)
                    except Exception, e:
                        LOG.error('Content could not be added', exc_info=True)
                    solr_connection.commit()
                    contents = list()
                    batch_num = 0
                else:
                    batch_num += 1

    # add the remaining batch 
    if args.batch_size and contents:
        solr_connection.add(contents)

    # commit everything to SOLR
    solr_connection.commit()

    if args.solr_optimize:
        LOG.debug('Optimizing Solr index')
        solr_connection.optimize()

    LOG.info('%d documents processed in %3.2f seconds' % (count, time.time()-ts))


def main():

    parser = argparse.ArgumentParser(description='Commandline parser')
    parser.add_argument('directory', metavar='<directory>', type=str,
                        help='Directory to be crawled')
    parser.add_argument('--solr-url', dest='solr_url', action='store',
                        default='http://localhost:8983/solr', 
                        help='SOLR server URL')
    parser.add_argument('--max-depth', dest='max_depth', action='store',
                        type=int,
                        default=None,
                        help='maximum folder depth')
    parser.add_argument('--batch-size', dest='batch_size', action='store',
                        type=int,
                        default=None,
                        help='Solr batch size')
    parser.add_argument('--tag', dest='tag', action='store',
                        type=str,
                        default='',
                        help='Solr import tag')
    parser.add_argument('--clear-all', dest='solr_clear', action='store_true',
                        default=False,
                        help='Clear the Solr indexes before crawling')
    parser.add_argument('--optimize', dest='solr_optimize', action='store_true',
                        default=False,
                        help='Optimize Solr index after import')
    parser.add_argument('--clear-tag', dest='solr_clear_tag', action='store',
                        default=None,
                        help='Remove all items from Solr indexed tagged with the given tag')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        default=False,
                        help='Verbose logging')
    parser.add_argument('--no-type-check', dest='no_type_check', action='store_true',
                        default=False,
                        help='Do not apply internal extension filter while crawling')

    args = parser.parse_args()
    crawl(args)

if __name__ == '__main__':
    main()
