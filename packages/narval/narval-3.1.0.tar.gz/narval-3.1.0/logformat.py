# coding: utf-8
"""utilities to turn raw logs into nice html reports (see format described below)

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

import logging
import re
from logilab.mtconverter import xml_escape
from cubicweb.utils import make_uid


REVERSE_SEVERITIES = {
    logging.DEBUG :   _('DEBUG'),
    logging.INFO :    _('INFO'),
    logging.WARNING : _('WARNING'),
    logging.ERROR :   _('ERROR'),
    logging.FATAL :   _('FATAL')
    }

# Properly formatted log are expected to use the following form:
#
#     {severity(int)}\t{filename}\t{line number}\t{msg text with potential new line}<br/>
#
# Messages that did not follow this convention are called "baldy formatted" and
# are displayed only at a debug level. However, we split the log stream on
# '<br/>' marker contained in "properly formated" log. As we can expect a
# message which didn't start properly (with the severity\tfilename\tlineno
# header) to not finish properly, it's likely that the bad ouput contained in
# the log stream does *not* end with a `<br\>` and that the `<br\>` used for
# splitting belongs to properly formated message. We can the try to recover any
# properly formatted messages embedded withing a wrongly formatted block.
#
# GOOD_MSG_STRICT_RE match the start of a perflectly formatted message. Any part
# of the stream matching it is considered a message without further processing.

# GOOD_MSG_START_RE match the start of propertly formatted message anywhere in
# block of text. (but we assume any propertly formatted message if preceded by a
# newline). We search for a match of GOOD_MSG_START_RE in the badly formatted
# block. If any match is found we split the block in two.

GOOD_MSG_STRICT_RE = re.compile(r'^[0-9]+\t.*\t.*\t')
GOOD_MSG_START_RE  = re.compile(r'^[0-9]+\t.*\t.*\t', re.MULTILINE)

def log_to_html(req, domid, data, w, defaultlevel='Info'):
    """format logs data to an html table

    log are encoded in the following format for each record:

      encodedmsg = u'%s\t%s\t%s\t%s<br/>' % (severity, path, line,
                                             xml_escape(msg))
    """
    req.add_css(('cubes.narval.css', 'cubicweb.tablesorter.css'))
    req.add_js(('cubes.narval.js', 'jquery.tablesorter.js'))
    if defaultlevel != 'Debug':
        req.add_onload('$("select.log_filter").val("%s").change();'
                       % req.form.get('log_level', defaultlevel))
    w(u'<form>')
    w(u'<label>%s</label>' % req._(u'Message Threshold'))
    w(u'<select class="log_filter" onchange="filter_log(\'%s\', this.options[this.selectedIndex].value)">'
      % domid)
    for level in ('Debug', 'Info', 'Warning', 'Error', 'Fatal'):
        w('<option value="%s">%s</option>' % (level, req._(level)))
    w(u'</select>')
    w(u'</form>')
    w(u'<table class="listing" id="%s">' % domid)
    w(u'<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (
        req._('severity'), req._('path or command'), req._('line'), req._('message')))
    all_msg = []
    #try to cure invalid msg:
    for msg in data.split('<br/>'):
        msg = msg.strip()
        if GOOD_MSG_STRICT_RE.search(msg) is not None:
            all_msg.append(msg)
        else:
            match = GOOD_MSG_START_RE.search(msg)
            if match is not None:
                # We found some real message inside, let's save it
                pos = match.start()
                junk = xml_escape(msg[:pos])
                all_msg.append(junk)
                all_msg.append(msg[pos:])
            else:
                # hopeless junk
                all_msg.append(xml_escape(msg))
    for msg_idx, record in enumerate(all_msg):
        record = record.strip()
        if not record:
            continue
        try:
            severity, path, line, msg = record.split('\t', 3)
            severityname = REVERSE_SEVERITIES[int(severity)]
        except (KeyError, ValueError):
            req.warning('badly formated log %s' % record)
            path = line = u''
            severity     = logging.DEBUG
            severityname = REVERSE_SEVERITIES[int(severity)]
            msg = record
        log_msg_id = 'log_msg_%i' % msg_idx
        w(u'<tr class="log%s" id="%s">' % (severityname.capitalize(),
                                           log_msg_id))
        w(u'<td class="logSeverity" cubicweb:sortvalue="%s">' % severity)
        data = {
            'severity': req._(REVERSE_SEVERITIES[int(severity)]),
            'title': _('permalink to this message'),
            'msg_id': log_msg_id,
        }
        w(u'''<a class="internallink" href="javascript:;" title="%(title)s" '''
          u'''onclick="document.location.hash='%(msg_id)s';">&#182;</a>'''
          u'''&#160;%(severity)s''' % data)
        w(u'</td>')
        w(u'<td class="logPath">%s</td>' % (path or u'&#160;'))
        w(u'<td class="logLine">%s</td>' % (line or u'&#160;'))
        w(u'<td class="logMsg">')
        SNIP_OVER = 7
        lines = msg.splitlines()
        if len(lines) <= SNIP_OVER:
            w(u'<pre class="rawtext">%s</pre>' % msg)
        else:
            # The make_uid argument have not specific meaning here.
            div_snip_id = make_uid(u'log_snip_')
            div_full_id = make_uid(u'log_full_')
            divs_id = (div_snip_id, div_full_id)
            snip = u'\n'.join((lines[0],
                               lines[1],
                               u'  ...',
                               u'    %i more lines [double click to expand]' % (len(lines)-4),
                               u'  ...',
                               lines[-2],
                               lines[-1]))
            divs = (
                (div_snip_id, snip, u'expand', "class='collapsed'"),
                (div_full_id, msg,  u'collapse', "class='hidden'")
            )
            for div_id, content, button, h_class in divs:
                text = _(button)
                js   = u"toggleVisibility('%s'); toggleVisibility('%s');" % divs_id

                w(u'<div id="%s" %s>' % (div_id, h_class))
                w(u'<pre class="raw_test" ondblclick="javascript: %s" '
                   'title="%s" style="display: block;">' % (js, text))
                w(u'%s' % content)
                w(u'</pre>')
                w(u'</div>')
        w(u'</td>')
        w(u'</tr>\n')
    w(u'</table>')
