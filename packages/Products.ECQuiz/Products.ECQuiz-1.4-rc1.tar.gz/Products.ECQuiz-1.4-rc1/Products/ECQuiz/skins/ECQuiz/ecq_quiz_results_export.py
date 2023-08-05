## Script (Python) "ecq_quiz_results_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format='tab'
##title=
##


#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
# $Id: ecq_quiz_results_export.py 245805 2011-10-23 19:08:23Z amelung $
#
# Copyright © 2004-2011 Otto-von-Guericke-Universität Magdeburg
#
# This file is part of ECQuiz.
#
# ECQuiz is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ECQuiz; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

ecq_tool = context.ecq_tool

I18N_DOMAIN = context.i18n_domain

target = context.getActionInfo('object/results')['url']
REDIRECT_URL = '%s' % target

if not REQUEST.has_key('ids'):
    msg = context.translate(
        msgid   = 'select_item_export',
        domain  = I18N_DOMAIN,
        default = 'Please select one or more items to export first.')

    context.plone_utils.addPortalMessage(msg)
    return context.redirect(REDIRECT_URL)

ERROR_FORMAT_MSG = context.translate(
    msgid   = 'unknown_format_export',
    domain  = I18N_DOMAIN,
    default = 'Unknown format. Cannot export.')

if not format:
    context.plone_utils.addPortalMessage(ERROR_FORMAT_MSG)
    return context.redirect(REDIRECT_URL)

format = format.lower()
exportFormatList = [o for o in context.RESULTS_EXPORT_FORMATS
                    if o[0].lower() == format]

if not exportFormatList:
    context.plone_utils.addPortalMessage(ERROR_FORMAT_MSG)
    return context.redirect(REDIRECT_URL)


exportFormat = exportFormatList[0]
#~ fileExt      = exportFormat[0]
colDelim     = exportFormat[1]
rowDelim     = exportFormat[2]
strStart     = exportFormat[3]
strEnd       = exportFormat[4]
escapeChar   = exportFormat[5]
encoding     = 'latin-1'

def escape(string):
    escaped = ''
    for c in string:
        if c in [escapeChar, strStart, strEnd]:
            escaped += escapeChar + c
        else:
            escaped += c
    return escaped

results = context.getResultsAsList(REQUEST['ids'])
exportCols = ['user_id', 'full_name', 'state', 'grade', 'score', 'max_score',
              'time_start', 'time_finish',]
if not results[0].has_key('grade'):
    exportCols.remove('grade')

NONE_STRING = context.translate(msgid   = 'N/A',
                                domain  = I18N_DOMAIN,
                                default = 'N/A')

output = ''
for row_dict in results:
    row = [row_dict[key] for key in exportCols]
    maxCol = len(row) - 1
    for i in range(0, maxCol+1):
        col = row[i]
        if col is None:
            col = NONE_STRING
        
        if same_type(col, '') or same_type(col, u''):
            # output as text if the content of the cell is a string
            output += strStart + escape(context.str(col)) + strEnd
        # no string --> no output as text
        elif same_type(col, 1.1):
            # i18n of fractional numbers
            output += escape(ecq_tool.localizeNumber("%.2f", col))
        else:
            output += escape(str(col))
        # If this is the last column of the row, append the row
        # delimiter.  Else, append the column delimiter.
        output += [colDelim, rowDelim][i == maxCol]

resultsString = context.translate(
    msgid   = 'results',
    domain  = I18N_DOMAIN,
    default = 'results')
    
filename = context.pathQuote(context.title_or_id()) + '_' + resultsString + '.' + format

RESPONSE.setHeader('Content-Disposition', 'attachment; filename=' + filename)
RESPONSE.setHeader('Content-Type', 'text/plain')

context.plone_utils.addPortalMessage("Done.")

# 'unicodeDecode()' is defined in the script (Python)
# Products/ECQuiz/skins/ECQuiz/unicodeDecode.py
return context.unicodeDecode(output).encode(encoding)
