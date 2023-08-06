#! -*- coding: utf-8 -*-

##
##  This file is part of infomedia library
##
##  Copyright (c) 2011-2012 Infomedia
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

from pprint  import pprint
from string  import rjust

import logging
logger = logging.getLogger(__name__)

def expansion(kk,define_set):
    if define_set is None:
        return kk
    k1=kk
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
    pkk = eval(kk)
    logger.debug("EXPANSION %s = %s = %s",k1,kk,pkk)
    return kk
        

def get_list(collection, sep=','):
    """
    Split the collection string in a list by separator sep

    @param collection: string containing one or more element 
    @type collection: unicode
    
    @param sep: separator character (defaults to ',')
    @type sep: unicode

    @returns: list of unicode
    """
    if collection:
        return [ el.strip() for el in collection.split(sep) ]

def boolean(instr):
    if instr is None: return False
    if isinstance(instr,(bool,int)): 
        return instr
    try:
        instr=eval(instr)
    except NameError, exc:
        pass
    if isinstance(instr,(str,unicode)):
        instr=instr.strip()
        if re.match('^yes|true|on|1$',instr,re.I): return True
        if re.match('^no|false|off|0$',instr,re.I): return False
    return bool(instr)


def get_struct(conf,taskname):
    section = taskname.upper().replace('_','-')
    if conf.has_section(section):
      tstruct = {}
      tstruct['label']=taskname
      for s in conf.options(section):
        tstruct[s]=get_conf_val(conf,section,s)
      return tstruct

    logger.warning("il file di configurazione non ha una sezione %s" % section )
    return None

def diff_dictionary(a,b):
    """
    riporta le differenze tra due dictionary
    """
    if a is None:
        return (b,True)
    if b is None:
        return (a,False)
    c = {}  
    d = False
    for k1,v1 in a.items():
        k = k1.encode('utf8','replace')
        v = v1.encode('utf8','replace')
        if not b.has_key(k):
            c[k]=(None,v)            
            continue
        
        if not b[k]==v:
            c[k]=(v,b[k])
            if k == "last updated": d = True

    return (c,d)

def needed(dataset,*needed_vars,**kw):
    """Throw ValueError if needed keys are not in the dataset

    :param dataset: the dictionary to check
    :type dataset: a dictionary

    :param needed_vars: list of key names
    :type needed_vars: list of strings

    :param error: optional name of error if should print a log line
    :type error: string

    """
    error="E:GENERIC:001"
    if kw.has_key('error'):
        error = kw['error']
    v = {}
    for k in needed_vars:
        v[k] = not dataset.has_key(k)
    w = [ k for k,v in v.items() if v ]
    if len(w)>0:                
        if len(w)==1:
            s = "%s -- No %s variable in dict" % (error,','.join(w))
        elif len(w)>1:
            s = "%s -- No %s variables in dict" % (error,','.join(w))
        raise ValueError, s
    return len(w)==0

def accepted(dataset,*accepted_vars):
    v = {}
    for k in sorted(dataset.keys()):
        v[k] = k in accepted_vars
    w = [ k for k,v in v.items() if not v ]
    if len(w)>0:             
        if len(w)==1:
            s = "La variabile %s non accettata" % ','.join(w)
        elif len(w)>1:
            s = "Le variabili %s non accettate" % ','.join(w)
        raise ValueError, s
    return len(w)==0

def keycond(key):
    name,cond = key,None
    if '|' in name:
        name,cond = name.split('|',1)
        logger.debug('ARETHA: %s - %s',name,cond)
    return name,cond

_COND_KEY = '__%s_COND'

class vdict(dict):
    """
    Dictionary
    
    """
    def __init__(self,*args,**kwargs):
        self._defines = None
        dict.__init__(self,*args,**kwargs)
        h = {}
        for k,v in self.items():
            del self[k]
            name,cond = keycond(k)
            if cond is not None:
                logger.debug('defining condition for name %s as %s',name,cond)
                self.set_condname(k,v)
            else:
                h[self._key(name)]=v

        dict.update(self,h)

    def get_cond(self,name):
        logger.debug("GET CONDITION ON %s",name)
        try:
            if self.has_key(_COND_KEY%name):
                if self._defines:                    
                    cond = [ boolean(self._defines.expand(
                        expansion(x,
                                  self._defines))) for x in self[_COND_KEY%name] ]
                else:
                    cond = [ boolean(x) for x in self[_COND_KEY%name]]
                    logger.debug("GET CONDITION ON %s GOT %s",name,cond)
                for c,v in zip(cond,self[name]):
                    if c:
                        return cond
        except SyntaxError, exc:
            pass
        return None

    def conditions(self,name):
        try:
            if self.has_key(_COND_KEY%name):
                if self._defines:
                    cond = [ boolean(self._defines.expand(
                        expansion(x,
                                  self._defines))) for x in self[_COND_KEY%name] ]
                else:
                    cond = [ boolean(x) for x in self[_COND_KEY%name]]
                return cond
        except SyntaxError, exc:
            pass
        return []

    def get_with_cond(self,name):
        logger.debug("GET CONDITION ON %s",name)
        try:
            if self.has_key(_COND_KEY%name):
                cond = self.conditions(name)
                for c,v in zip(cond,self[name]):
                    if c: return v
        except SyntaxError, exc:
            pass
        return None

    def has_cond(self,name):
        return dict.has_key(self,_COND_KEY%name)

    def set_with_cond(self,name,value,cond):
        logger.debug('SETTING %s=%s in condition %s',name,value,cond)
        if value:
            if cond:
                if not self.has_cond(name):
                    self[_COND_KEY%name] = []
                    self[_COND_KEY%name].append(cond)
                    self[name]=[]
                    self[name].append(value)
                    return value
                else:
                    for i,c in enumerate(self[_COND_KEY%name]):
                        if c==cond:
                            self[name][i]=value
                            return value
                    self[_COND_KEY%name].append(cond)
                    self[name].append(value)
                    return value
        dict.__setitem__(self,name,value)
                    
    def set_condname(self,name,value):
        name,cond=keycond(name)
        return self.set_with_cond(name,value,cond)

    def del_cond(self,name):
        if self.has_cond(name):
            cond = self.get_cond(name)
            del self[_COND_KEY%name]
            return cond

    def _key(self,key):
        return key
    
    def _ret_valcond(self,name,f,*args):
        if self.has_cond(name):
            logger.debug("Condition for %s is %s",name,cond)
            if self.get_cond(name):
                return f(self,self._key(name),*args)
            return None
        else:
            return f(self,self._key(name),*args)

    def __getitem__(self,name):
        if name:
            return dict.__getitem__(self,self._key(name))

    def __setitem__(self,name,value):
        # logger.debug("SETITEM %s<-%s",name,value)
        if '|' in name:
            cond = self.set_condname(self._key(name),value)
        else:
            cond =  dict.__setitem__(self,self._key(name),value)
        return cond

    def __contains__(self,item):
        return self._ret_valcond(item,dict.__contains__)

    def has_key(self,name,defines=None):
        # logger.debug("Has key for %s -> %s/%s",
        #             name,
        #             self._defines is not None,
        #             self.has_cond(name))
        # logger.debug("> for %s ",name)

        if defines:
            self._defines = defines

        if self.has_cond(name):
            for c in self.conditions(name):
                if c:
                    return True
            return False

        return dict.has_key(self,self._key(name))

    def has(self,name,*values,**kw):
        if not values or len(values)==0:
            return None
        flags=re.I
        negate = False
        if kw.has_key('flags'):
            flags=kw['flags']
        if kw.has_key('negate'):
            negate=kw['negate']
        if self.has_key(name):
            S=self[name]
            for _v in values:
                if re.match(_v,S,flags) and not negate:
                    return _v


    def get_bool(self,key,default=False):
        value = boolean(self.xget(self._key(key)))
        if value is not None:
            return value
        return default

    def xget_bool(self,key,default=False):
        return self.get_bool(key,default)

    def xget_dictlist(self,key,default=None,
                  negate=False,
                  delete=False,
                  create=False,
                  defines=None,
                  section=None,sep=','):
        dictnames = self.xget_list(key,default,negate,delete,create,defines,section)
        pprint(dictnames)
        return self.select(*dictnames)
    
    def xget_list(self,key,default=None,
                  negate=False,
                  delete=False,
                  create=False,
                  defines=None,
                  section=None,sep=','):
        v = self.xget(key,default,negate,delete,create,defines,section)
        if v:
            return get_list(v,sep=sep)

    def xget_dict(self,key,default=None,
                  negate=False,
                  delete=False,
                  create=False,
                  defines=None,
                  section=None):
        v = self.xget(key,default,negate,delete,create,defines,section)
        if v:
            return self.__class__(v)

    def xget(self,key,default=None,
                      negate=False,
                      delete=False,
                      create=False,
                      defines=None,
                      section=None):
        """Get a value from the vdict o a sub dict

        @param key: label to find
        @type key: string

        @param default: default value if key not exists

        @param negate: return default if key not found
        @param delete: delete key if exists
        @param create: create key if not exists
        @param defines: expand key from define set
        @param section: take key from sub section
        """
        key = self._key(key)

        if defines:
            self._defines = defines

        if '[' in key:
            m = re.match('^\[([^]]+)\](.+)$',key,re.I)
            if m:
                section = m.group(1)
                key = m.group(2)

        if section:
            if self.has_key(section):
                return vdict(self[section]).xget(self._key(key),
                                                 default,
                                                 negate,
                                                 delete,
                                                 create,
                                                 defines)
            return None

        v = grep("^%s$"%key,self)

        if v and not negate:
            ret = v[0]

            if self.has_key(ret):                    
                if self.has_cond(ret):
                    val = self.get_with_cond(ret)
                else:
                    val = self[ret]

                if delete:
                    del self[ret]
                if isinstance(val,(basestring)):
                    return val.strip()
                return val
            if create:
                logger.error('Trying to create a conditioned out value')
                raise ValueError, ret
            return default
        else:
            if create:
                self[self._key(key)]=default
            return default

    def select(self,*regexps,**kw):
        """
        Select variables name with a regular expression
        
        @param regexps: a regular expression matching the name
        @type regexps: list of unicode
        @returns: udict or None
        """
        R = True
        if kw.has_key('regexp'):
            R = kw['regexp']
        res = udict()
        for _regexp in regexps:
            model = _regexp                
            if not R:
                model = "^"+model+"$"
            names = grep(model,self.keys())
            if names:
                for name in names:
                    res.update(udict({name:self[name]}))
        return res

    def select_as_list(self,*regexps):
        """
        Select variables name with a regular expression
        
        @param regexps: a regular expression matching the name
        @type regexps: list of unicode
        @returns: udict or None
        """
        res = list()
        for regexp in regexps:
            names = grep(regexp,self.keys())
            if names:
                res.extend([ self[name] for name in names])
        return res

    def select_nulls(self,*regexps):
        """
        Select variables name with a regular expression
        
        @param regexps: a regular expression matching the name
        @type regexps: list of unicode
        @returns: udict or None
        """
        res = udict()
        for regexp in regexps:
            names = grep(regexp,self.keys())        
            if not names:
                res.update(udict([(name,None) for name in names]))
        return res

    def remove(self,*regexps):
        """
        Remove keys with regexps

        @param regexps: list of regexp matching keys
        """
        res = udict()
        for regexp in regexps:
            names = grep(regexp,self.keys())
            if names:
                for name in names:
                    del self[name]
                    if self.has_cond(name):
                        self.del_cond(name)
        return self

    def purge(self,key):
        if self.has_key(key):
            del self[key]
            if self.has_cond(key):
                self.del_cond(key)


class udict(vdict):
        def __init__(self,*args,**kwargs):
            vdict.__init__(self,*args,**kwargs)
        def _key(self,key):
            return key.upper()
        def update(self,indict):
            h = udict(indict)
            vdict.update(self,h)

                
class ldict(vdict):
        def __init__(self,*args,**kwargs):
            vdict.__init__(self,*args,**kwargs)
        def _key(self,key):
            return key.lower()
        def update(self,indict):
            h = ldict(indict)
            vdict.update(self,h)

def fmt_dict(d,cond=lambda x,y: True):
    return ','.join(["%s=%s" % (str(k),str(v)) for k,v in d.items() if cond(k,v)])

def dictview(d,sep=','):
    if d is None: return u"None"
    if len(d)==0: return u"Empty"

    if isinstance(d,basestring): 
        return d
    if isinstance(d,(list,tuple)):
        s = u"[len=(%d)|" % len(d)    
        s += u','.join([dictview(v) for v in d])
        s += u"]"
        return unicode(s)

    # now is dict
    L = [ len(k) for k in d.keys()]

    if len(L)==0:
        return 'EMPTY'

    lrg = max([ len(k) for k in d.keys()])

    s = "{"
    for k,v in sorted(d.items()):
        if isinstance(v,dict):
            if len(v)==0:
                s += " None"
                continue
            s+="%s = {  \n" % rjust(k,lrg)
            lrg1 = max([ len(k1) for k1 in v.keys()])
            for c,w in sorted(v.items()):
                s+=" %s %s = %s | %s \n"  % (rjust(' ',lrg),rjust(c,lrg1),w,type(w))
            s+=" %s }\n"%( rjust(' ',lrg) )
        else:
            s+="%s = %s | %s\n"%( rjust(k,lrg),v,type(v))
    s += "}"
    return s
#    lrg = max([ len(k) for k in d.keys()])
#    s = "{len=(%d)%s " % (len(d),sep)
#    s += sep.join([" %s=%s" % (rjust(k,lrg),v) for k,v in sorted(d.items())])
#    s += " }"
#    return s

def logdict(func,info,d):
    func('%s -- %s %s',info,type(d), dictview(d))


def grep(string,aList,*flags):
    """ seleziona le stringhe che rispettano l'espressione regolare della lista di stringhe aList"""
    expr = re.compile(string,*flags)
    if isinstance(aList, (list,tuple)):
        return filter(expr.search,aList)
    if isinstance(aList, (dict,udict,ldict)):
        return filter(expr.search,aList.keys())

def select(aDict,*regexps):
    """
    Select variables name with a regular expression
    
    @param regexps: a regular expression matching the name
    @type regexps: list of unicode
    @returns: udict or None
    """
    res = udict()
    for regexp in regexps:
        names = grep(regexp,aDict.keys())
        if names:
            res.update(udict([(name,aDict[name]) for name in names]))
    return res
        
def compose_dicts(dicts,accept=[],klass=udict):
    """Each arg is a dict. Returns composition of dicts in reverse order"""
    _dict=klass()
    _dict = klass(dicts[0])
    for _a in dicts[1:]:
        if accept and len(accept)>0:
            _D=select(_a,*accept)
        else:
            _D=a
        _dict.update(klass(_D))
    _dict = extend_booleans(_dict)
    return _dict

def extend_booleans(_dict):
    klass = _dict.__class__
    _ret  = klass()
    
    for key,value in _dict.items():
        if isinstance(value,basestring):

            if re.match('^yes|on|true|1$',value,re.I):
                _val = klass({'ACTIVE': True, key: value})
                _ret.update(klass({key:_val}))
                continue

            if re.match('^no|off|false|1$',value,re.I):
                _val = klass({'ACTIVE': False, key: value})
                _ret.update(klass({key:_val}))
                continue

        _ret.update(klass({key:value}))

    return _ret


__all__ = """
 expansion
 get_list
 boolean
 get_struct
 diff_dictionary
 needed
 accepted
 keycond
 vdict
 udict
 ldict
 dictview
 logdict
 grep
 select
 compose_dicts
 extend_booleans
""".split()
