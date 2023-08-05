#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
# $Id: ecq_quiz_wiki_convert.py 245805 2011-10-23 19:08:23Z amelung $
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

"""This script is called when the wiki_edit tab is loaded"""

REQUEST  = context.REQUEST
RESPONSE = REQUEST.RESPONSE

# Make sure the skript is called inside a ECQuiz context:
if "ECQuiz" in str(context):
  return context.convertQuiz(context)
else:
  return "This skript runs not inside a ECQuiz context"
