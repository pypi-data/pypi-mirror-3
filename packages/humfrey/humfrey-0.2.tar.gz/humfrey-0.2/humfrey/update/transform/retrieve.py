from __future__ import with_statement

import logging
import mimetypes
import os
import urllib2

from humfrey.update.transform.base import Transform

logger = logging.getLogger(__name__)

class Retrieve(Transform):
    mimetype_overrides = {
        'application/xml': 'xml',
    }

    def __init__(self, url):
        self.url = url

    def execute(self, transform_manager):
        logger.info("Attempting to retrieve %r" % self.url)
        request = urllib2.Request(self.url)
        request.headers['Accept'] = "application/rdf+xml, text/n3, text/turtle, application/xhtml+xml;q=0.9, text/html;q=0.8"
        response = urllib2.urlopen(request)
        logger.info("Response received for %r" % self.url)
        
        content_type = response.headers.get('Content-Type', 'unknown/unknown')
        content_type = content_type.split(';')[0].strip()
        extension = self.mimetype_overrides.get(content_type) \
                 or (mimetypes.guess_extension(content_type) or '').lstrip('.') \
                 or (mimetypes.guess_extension(content_type, strict=False) or '').lstrip('.') \
                 or 'unknown'
        
        logger.info("Response had content-type %r; assigning extension %r" % (content_type, extension))
            
        with open(transform_manager(extension), 'w') as output:
            transform_manager.start(self, [input], type='identity')
            block_size = os.statvfs(output.name).f_bsize
            while True:
                chunk = response.read(block_size)
                if not chunk:
                    break
                output.write(chunk)
            transform_manager.end([output.name])
            
            logger.info("File from %r saved to %r" % (self.url, output.name))
            return output.name