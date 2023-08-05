# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.conf import settings
from django.utils.log import getLogger
logger = getLogger('django.request')
#logger = getLogger('django')
try:
    import lxml.html
    from   lxml.etree import tostring
except ImportError:
    logger.warning('Forbidden (lxml midule not installed): %s' % request.path,
        extra={
            'status_code': 404,
        }
    )

CRLF2UNIX = re.compile(r'\r\n|\n\r?',re.M)

class HTML2eltreeMiddleware(object):
    def process_response(self, request, response):
        mmm = {}
        response.lxml_etree = None
        he = response._headers.get('content-type')
        if not he or response.status_code != 200 :
            return response
        c = he[1].split(';')[0]
        #print(c)
        if c in ('text/html', 'application/xhtml+xml', 'application/xml'):
            #doc = lxml.html.fromstring(doc.decode('utf-8'))
            doc = '{}'.format(response.content.decode('utf-8'))
            doc = CRLF2UNIX.sub('\n',doc)
            doc = lxml.html.fromstring(doc)
            response.lxml_etree = doc
        else:
            pass
        return response
#
class Eltree2HTMLMiddleware(object):
    def process_response(self, Request, Response):
        def indent(elem, level=0):
            i = '\n' + level * '  '
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + '  '
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        #
        doc = Response.lxml_etree
        if doc is None:
            #ErrResponse(Request,Response,'NO lxml_etree in reponse!')
            return Response
        indent(doc)
        Response.content = lxml.html.tostring(doc.getroottree(),
            method='xml',
            pretty_print=True,
            encoding='utf-8',
        )
        #print(type(Response.content))
        return Response
#


