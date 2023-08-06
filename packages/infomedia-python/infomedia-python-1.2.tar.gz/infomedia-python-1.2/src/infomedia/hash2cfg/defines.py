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

from os import getenv,environ
from datetime import datetime
from pprint import pprint
from os.path      import (basename, expanduser, join,
                          dirname, exists, expandvars,
                          isdir)

from infomedia.collections import vdict,udict,logdict
from infomedia.options     import Options

import logging
logger=logging.getLogger(__name__)

# defines, functions, processor and macro
_date = datetime.now()

# DEFINES
DEFAULT_DEFINES = {
    'THISMONTH':  str(_date.month),
    'THISYEAR':   str(_date.year),
    'TYEAR':      str(_date.year)[2:],
    'PREVYEAR':   str(_date.year-1),
    'PREVVYEAR':  str(_date.year-2),
    'PREVVVYEAR': str(_date.year-3),
    'NEXTYEAR':   str(_date.year+1),
    'SRIDATA':    getenv('SRIDATA'),
    'YUPD':       str(0),
    'UPDATE':     str(0),
    'DONT_UPDATE':str(1),
    'NUM':        str(0),
    'DATE':      _date.strftime('%Y%m%d'),
    'THISDATE':  _date.strftime('%d/%m/%Y'),
    'LONG_DATE': _date.strftime('%d %B %Y'),
    'DS_DATE':   _date.strftime('%Y-%m-%d')
}

## FUNCTIONS IN TABLE DEFINITION
## 
mnth = [ '_(Jan)', '_(Feb)', '_(Mar)',
	 '_(Apr)', '_(May)', '_(Jun)',
	 '_(Jul)', '_(Aug)', '_(Sep)',
	 '_(Oct)', '_(Nov)', '_(Dec)' ]
macro_last_year = False
def macro_month(*args):
    """month from 0->Jan to 11->Dec"""
    ev = int(args[0])-1
    return (mnth[ev%12],1,"c")
def macro_fyear(*args):
    """FYEAR(YEAR,MONTH)
    returns
    \multicolumn{n}{c}{$THISYEAR}
    or
    empty if
    """
    global macro_last_year
    month = int(args[1])-1
    year  = int(args[0]) - ( 1 if month < 0 else 0 )
    remain= int(args[2])
    _date = datetime.now()
    Y = _date.year
    M = _date.month
    logger.debug("{FYEAR} m/d - remain - M/Y = %d/%d - %d - %d/%d",
                 month,year,remain,M,Y)
    if year==Y:
        macro_last_year = False
        if month == 0:
            # emit a multicolumn for remaining months
            if remain == 1:
                return (str(year),1,"c")
            else:
                return (str(year),remain,"c")
    else:
        if macro_last_year == False:
            macro_last_year = True
            return (str(year),-month,"c")

    return None

def macro_get(name,*args):
#    logger.debug('{MACRO GET} %s > %s',name,args)
    n = 0
    if args and args[0]:
        m = re.match('^(-?[0-9]+)$',args[0])
        if m:
            n = int(m.group(1))
    m = re.match('^[A-Z][A-Z0-9_]*$',name)
    if m:        
        if dataset.has_key(name):
            TS = dataset[name]
            return (unicode("%.1f"%TS.data[n]),1,"c")

def macro_getdate(name,*args):
#    logger.debug('{MACRO GET} %s > %s',name,args)
    n = 0
    if args and args[0]:
        m = re.match('^(-?[0-9]+)$',args[0])
        if m:
            n = int(m.group(1))
    m = re.match('^[A-Z][A-Z0-9_]*$',name)
    if m:        
        if dataset.has_key(name):
            TS = dataset[name]
            return (unicode(TS.dates[n]),1,"c")

macro_fncs = { 'MONTH': macro_month ,
               'FYEAR': macro_fyear ,
               'GET': macro_get ,
               'GETDATE': macro_getdate ,
               }

name    = None
spec    = None
dataset = None
options = None


def macro_rerepl(matchobj):
    g = [ _m for _m in matchobj.groups()]
    f= g.pop(0)
    res = macro_fncs[f](*g)
    if res:
        (msg,n,c) = res
        return "#%s#%s#%s#" % (msg,n,c)

def expandfuncs(string,_name=None,_spec=None,_dataset=None,_options=None,unfold=False):
    global name, spec, dataset, options

    if isinstance(string,(tuple,list)):
        return string
        # expandlistfunc(string,_name,_spec,_dataset,_options,unfold)


    string=unicode(string)
    if _name: name = _name
    if _spec: spec = _spec
    if _dataset: dataset = _dataset
    if _options: options = _options

    # logger.debug('{EXPANDFUNCS} W:%s N:%s S:%s D:%s O:%s',string,type(name),type(spec),type(dataset),type(options))
        
    
    _ttt = unicode(string)

    if len(_ttt)==0:
        return string

    if '%' not in string:
        return _ttt

    # logger.debug('{EXPANDFUNCS} 2:%s',_ttt)

    m = re.search('%([A-Z]+)\(([^),]+)(,[^,)])*\)',_ttt,re.IGNORECASE)
    if m:
#        logger.debug('{EXPANDFUNCS} M:%s',m.groups())
        _tto=_ttt
        while '%' in _ttt:
            _ttt=re.sub('%([A-Z]+)\(([^,)]+)(?:,([^,)]+))?(?:,([^,)]+))?\)',
                        macro_rerepl,
                        _ttt,
                        re.IGNORECASE)
            if _ttt is None or _ttt == _tto:
                break
            _tto=_ttt
    if _ttt:
        if unfold:
            _ttt=re.sub('#([^#]+)#[^#]+#[^#]+#',
                        '\\1',
                        _ttt,
                        re.IGNORECASE)
        logger.debug("EXPANDFUN- %s --> %s",string,_ttt)
        return _ttt

def expandlistfunc(string,_name=None,_spec=None,_dataset=None,_options=None,unfold=False):
    return [ expandfunc(x,_name,_spec,_dataset,_options,unfold) for x in string ]



class DefineSet(udict):
#    _we_are_one = {}

    def __init__(self,indict=None):
        udict.__init__(self)
        self._varprog = None
        self.setUp()
        if indict:
            self.update(indict)

    def report(self):
        s=""
        for k,v in self.items():
            s+="%s=%s\n"%(k,v)
        return s

    def update(self,indict):
        h = udict(indict)
        vdict.update(self,h)
        if hasattr(indict,'_vaprog'):
            self._varprog = indict._vaprog
        else:
            import re
            self._varprog = re.compile(r'\$(\w+|\{[^}]*\})')
            
    def setUp(self):
        self.update(environ)
        self.update(DEFAULT_DEFINES)
        self._varprog = None

    def update_from_strings(self,definitions):
        if definitions:
            self.update(udict([ v.split('=') for v in definitions]))

    def expand(self,path):
        """Expand parameters of form $var and ${var}.  Unknown variables
        are left unchanged.

        @param path: path string to expand
        @type path: unicode

        @returns: the path string with parameters expanded
        """
        # logdict(logger.debug,'{EXPANDDEFINES} for path %s'%path,self)

        if len(self)==0:
            self.setUp()

        if isinstance(path,udict):
            return udict([ (k,self.expand(unicode(v))) for k,v in path.items() ])
        
        if '$' not in path:
            return path

        if not self._varprog:
            import re
            self._varprog = re.compile(r'\$(\w+|\{[^}]*\})')

        i = 0
        while True:
            m = self._varprog.search(path, i)
            if not m:
                break
            i, j = m.span(0)
            name = m.group(1)
            if name.startswith('{') and name.endswith('}'):
                name = name[1:-1]
            if name in self:
                tail = path[j:]
                path = path[:i] + unicode(self[name])
                i = len(path)
                path += tail
            else:
                i = j
        return path


class MacroSet(udict):
    pass

define_set = DefineSet()

def expansion(kk):
    ### Questo applica di nuovo l'espansione
    pkk = None
    if '$' in kk:
        kk=define_set.expand(kk)
    def rerepl(matchobj):
        g=matchobj.group(1)
        ev = eval(g)
        return unicode(ev)
    while '((' in kk:
        kk=re.sub('\(\(([-+*/0-9. ]+)\)\)',
                  rerepl,
                  kk)
        if kk == pkk:
            break
    pkk = kk
    return kk


__all__ = """
 expandfuncs
 expandlistfunc
 define_set
 expansion
 DEFAULT_DEFINES
""".split()
