#! -*- coding: utf-8 -*-

##
##  This file is part of infomedia framework library
##
##  Copyright (c) 2011-2012 Infomedia Foundation
##
##  Author: Emmanuele Somma (emmanuele_DOT_somma_AT_infomedia_DOT_it)
##		  
##  Any parts of this program derived from this project,
##  or contributed by third-party developers are copyrighted by their
##  respective authors.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA
##
##

import re

from infomedia.collections import grep,udict

import logging
logger=logging.getLogger(__name__)

class Options(object):
    _we_are_one = {}

    def __init__(self,*args,**kw):
        self.__dict__ = self._we_are_one
        for k,v in kw.items():
            setattr(self,k,v)
            
    def select(self,*regexps,**kw):
        """
        Select variables name with a regular expression
        
        :param regexps: a regular expression matching the name
        :type regexps: list of unicode
        :rtype: udict or None
        """
        R = True
        if kw.has_key('regexp'):
            R = kw['regexp']
        res = {}
        for _regexp in regexps:
            model = _regexp                
            if not R:
                model = "^"+model+"$"
            names = grep(model,self.__dict__.keys())
            if names:
                res.update(udict([(name,self.__dict__[name]) for name in names]))
        return res


__all__ = """
 Options
""".split()
