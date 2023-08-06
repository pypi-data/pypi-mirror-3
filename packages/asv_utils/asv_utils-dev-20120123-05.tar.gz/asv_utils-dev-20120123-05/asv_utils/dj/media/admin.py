# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_utils.dj import reverse_lazy
from asv_utils.dj.media import settings as AME
#---------------------------------------------------------------
#---------------------------------------------------------------
asv_media__lib__jQuery = AME.ASV_MEDIA__JQUERY_LOCATION
asv_media__lib__jQueryUI = AME.ASV_MEDIA__JQUERYUI_LOCATION
asv_media__lib__jQueryUI_css = AME.ASV_MEDIA__JQUERYUI_CSS_LOCATION
asv_media__lib__jQueryCookie = reverse_lazy('asv_media__media', args=('lib/jquery.cookie.min.js',))
asv_media__lib__jQueryJson = reverse_lazy('asv_media__media', args=('lib/jquery.json.min.js',))
asv_media__lib__Colorbox = reverse_lazy('asv_media__media', args=('lib/colorbox/jquery.colorbox-min.js',))
asv_media__lib__Colorbox_css = reverse_lazy('asv_media__media', args=('lib/colorbox/colorbox.css',))
#---------------------------------------------------------------
asv_media__admin__inlines_js = reverse_lazy('asv_media__media', args=('js/admin__inlines.js',))
#-------------------------------------------------------
DEFAULT_MEDIAFILES = {
        'text/css': (asv_media__lib__jQueryUI_css,),
        'text/javascript': (asv_media__lib__jQuery, asv_media__lib__jQueryUI, asv_media__lib__jQueryCookie, asv_media__lib__jQueryJson,),
}
#---------------------------------------------------------------
#---------------------------------------------------------------