# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.conf import settings as dj_settings
from lxml.builder import E
from asv_utils.dj.media.admin import *
from django.utils.log import getLogger
logger = getLogger('django.request')

#-------------------------------------------------------
#-------------------------------------------------------
MediaProcessing = {
    'text/css': (
        { 'LIB': 'JQUERYUI',
          'R': (
            re.compile(r'\/([\.\d]+)+\/themes\/\w+\/jquery-ui.css$',re.I),
          )
        },
    ),
    'text/javascript': (  # PASS sections need be first
        { 'LIB':'DJJQUERY',
          'R':(
              re.compile(
                re.sub(r'/+','/',r'{}/js/jquery(\.min)*\.js$'.format(dj_settings.ADMIN_MEDIA_PREFIX))
              ),
          ),
          'PASS':True,
        },
        { 'LIB':'JQUERY',
          'R':(
              re.compile(r'jquery(\.min)*\.js$',re.I),
              re.compile(r'\/([\.\d]+)*\/jquery(\.min)*\.js$',re.I),
              re.compile(r'jquery([-\.\d]+)*(\.min)*\.js$',re.I)
            ),
        },
        { 'LIB': 'JQUERYUI',
          'R':(
              re.compile(r'jquery-ui(\.min)*\.js$',re.I),
              re.compile(r'\/([\.\d]+)*\/jquery-ui(\.min)*\.js$',re.I),
              re.compile(r'jquery-ui([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
        { 'LIB':'JQUERYCOOKIE',
          'R':(
              re.compile(r'jquery[\.\_]+cookie([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
        { 'LIB': 'JQUERYJSON',
          'R':(
              re.compile(r'jquery[\.\_]+json([-\.\d]+)*(\.min)*\.js$',re.I),
          ),
        },
    )
}
#-------------------------------------------------------
#-------------------------------------------------------
class AddSomeJS(object):
    MediaFiles = []
    def process_request(self, Request):
        # reverse do not work in process_response :(
        # We need use it here :(
        if not self.MediaFiles:
            for T in DEFAULT_MEDIAFILES:
                for i in DEFAULT_MEDIAFILES[T]:
                    EEE = None
                    if T == 'text/css':
                        EEE = E('link',
                            rel  = 'stylesheet',
                            type = 'text/css',
                            href = '{}'.format(i),
                        )
                    elif T == 'text/javascript':
                        EEE = E('script',
                            type = 'text/javascript',
                            src = '{}'.format(i),
                        )
                    else:
                        continue
                    if EEE is not None:
                        self.MediaFiles.append(EEE)

    def process_response(self, Request, Response):
        doc = Response.lxml_etree
        if doc is None:
            return Response
        hh = doc.xpath('head')[0]
        pos = 0
        for i in self.MediaFiles:
            hh.insert(pos, i)
            pos += 1
        return Response
#-------------------------------------------------------
#-------------------------------------------------------
class FilterSomeJS(object):
    def process_response(self, Request, Response):
        ProcessingResult = {}
        def ErrResponse(Req, Resp, txt):
            if dj_settings.DEBUG:
                print('asv_utils.media::{}::{}'.format(Req.path,txt))
        mmm = {}
        doc = Response.lxml_etree
        if doc is None:
            #ErrResponse(Request,Response,'NO lxml_etree in reponse!')
            return Response
        hh = doc.xpath('head')[0]
        ts=('text/css','text/javascript')
        for TypeTag in ts:
            mmm[TypeTag]=[]
        k=0
        for TypeTag in ('link','script'):
            ll = hh.xpath(TypeTag)
            for LIB in ll:
                t=LIB.attrib.get('type')
                if t and t==ts[k]:
                    uri=LIB.attrib.get('src',LIB.attrib.get('href'))
                    if uri:
                        mmm[ts[k]].append((LIB,uri,))
            k+=1
        #ErrResponse(Request,Response,'**{}'.format(mmm))
        for T in ts:
            q = ProcessingResult.get(T)
            if not q:
                ProcessingResult[T] = {}
            for H in mmm[T]:
                for Rg in MediaProcessing[T]:
                    OK = False
                    q = ProcessingResult[T].get(Rg['LIB'])
                    if not q:
                        ProcessingResult[T][Rg['LIB']] = []
                    for R in Rg['R']:
                        if R.search(H[1]):
                            if Rg.get('PASS'):
                                pass
                            else:
                                ProcessingResult[T][Rg['LIB']].append({
                                    'EL': H[0],
                                    'URI': H[1],
                                })
                            OK = True
                            break
                    if OK:
                        break
        #ErrResponse(Request,Response,'=={}'.format(ProcessingResult))
        for TypeTag in ProcessingResult:
            if not ProcessingResult[TypeTag]:
                continue
            #print(TypeTag)
            for LIB in ProcessingResult[TypeTag]:
                if not ProcessingResult[TypeTag][LIB]:
                    continue
                #print('  {}'.format(LIB))
                kk = 0
                for k in ProcessingResult[TypeTag][LIB]:
                    #print('    {}'.format(k))
                    EE = k['EL']
                    EE.clear()
                    EE.getparent().remove(EE)
                    kk+=1
        return Response
#-------------------------------------------------------
#-------------------------------------------------------
