# -*- coding: utf-8 -*-
from __future__ import unicode_literals

ASV_MEDIA__HTML_RENDER_METHOD = 'html'
ASV_MEDIA__HTML_DOCTYPE  = 'html4'
ASV_MEDIA__HTML_ENCODING = 'utf-8'
ASV_MEDIA__HTML_DOCTYPES = {
    'html5': '<!DOCTYPE HTML>',
    'html4': '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',
    'xhtml': '<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
}
ASV_MEDIA__HTML_DOCTYPES['html'] = ASV_MEDIA__HTML_DOCTYPES['html4']
ASV_MEDIA__HTML_DOCTYPES['xml']  = ASV_MEDIA__HTML_DOCTYPES['xhtml']

ASV_MEDIA__JQUERY_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js'
ASV_MEDIA__JQUERYUI_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js'
ASV_MEDIA__JQUERYUI_CSS_LOCATION = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/themes/redmond/jquery-ui.css'

#ASV_MEDIA__DEFAULT_MEDIAFILES = False