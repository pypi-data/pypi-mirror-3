#! /usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright 2011-2012 by Infomedia Foundation

# @OPENSOURCE_HEADER_START@
# @OPENSOURCE_HEADER_END@

##  Author: Emmanuele Somma (emmanuele_DOT_somma_AT_infomedia_DOT_it)

__author__ = 'emmanuele.somma@infomedia.it (Emmanuele Somma)'
__date__ = '02 Nov 2011'
__version__ = '3.0'
__status__ = "to review"

# Standard imports
import codecs
import os
import re

from StringIO     import StringIO
from exceptions   import Exception
from os.path      import expanduser, join, dirname, exists, expandvars
from pprint       import pprint
from stat         import *
from types        import *

# 3rd party libraries
from initools.configparser import *
from initools.iniparser import ParseError

# Internal imports
from infomedia.options                import Options
from infomedia.collections            import udict,ldict,logdict
from infomedia.hash2cfg.defines       import define_set

# Globals
import logging
logger = logging.getLogger(__name__)

class Error(Exception):
    pass

class ConfigNotProtectedDBError(Error):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "Errore: Il backend %s non esiste" % self.msg

class ConfigNotProtectedError(Error):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "Errore: Il file di configurazione %s non ha le debite protezioni" % self.msg

class ConfigNotExistsError(Error):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "Errore: Il file di configurazione %s non esiste" % self.msg

class NoSessionInConfigFileError(Error):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return "Errore: Il file di configurazione  %s non esiste" % self.msg

include_l = re.compile('^#include\s+"(?P<path>[^":]+)"\s+$')
include_g = re.compile('^#include\s+\<(?P<path>[^<>:]+)\>\s+$')

def _get_temp_file_with_include(fname):
    base = dirname(fname)
    ifp = codecs.open(fname, "r", "utf8")
    lines = ifp.readlines()
    nlines = []
    for l in lines:
        m1 = include_l.match(l)        
        m2 = include_g.match(l)        
        if m1:
            ifname = m1.group('path')
            f = join(base,ifname)
            if exists(f):
                nl = codecs.open(f, "r", "utf8").readlines()
                nlines.extend(nl)                
            else:
                raise ValueError, 'local included files %s not exists in dir' % f
        elif m2:
            IDIR = os.getenv('SRISTATINPUTS')
            if IDIR:
                dirs = IDIR.split(':')
                ifname = m2.group('path')
                for d in dirs:
                    f = join(d,ifname)
                    if exists(f):
                        nl = codecs.open(f, "r", "utf8").readlines()
                        nlines.extend(nl)
                        break
                else:
                    raise ValueError, 'global included files %s not exists in input path' % ifname
            else:
                raise ValueError, 'SRISTATINPUTS empty cannot %s' % l
        else:
            nlines.append(l)    
    fp = StringIO()
    fp.write(''.join(nlines))
    fp.seek(0)
    return fp


def hash2cfg(data,fname,base=None):
    """
    Write into C{fname} a configuration file based on the
    configuration dictionary

    @param data: configuration dictionary
    @type data: dictionary

    @param fname: name of the file
    @type fname: unicode

    @param base: base section
    @type base: unicode
    """
    def hvalue(v):
        def hhvalue(v):
            if type(v) == NoneType:
                return 'null'
            if type(v) == BooleanType:
                if v: 
                    return "true"
                return "false"
            return v
        if type(v)==ListType:
            r = []
            for v1 in v:
                r.append(hhvalue(v1))
        return hhvalue(v)

    if base:
        logger.warn("Hashing to a base %s", base)

    if type(data)!=DictType:
        logger.warn("Argument is not a dictionary")
        return None
    xcfg = ConfigParser()
    for k,v in data.items():
        if type(v)==DictType: 
            xcfg.add_section(k)
            for ki,vi in v.items():
                xcfg.set(k,ki,hvalue(vi))
        elif type(v)==TupleType or type(v)==ListType: 
            xcfg.add_section(k)
            if type(v[0])==StringType or type(v[0])==UnicodeType:
                xcfg.set(k,'kind','list')
                #v=hvalue(v)
                xcfg.set(k,'list',','.join(v))
            if type(v[0])==DictType:
                xcfg.set(k,'kind','set')
                names = [ "name%02d" % i for i in range(0,len(v)) ]
                xcfg.set(k,'set',",".join(names))
                xcfg.set(k,'keys',','.join(v[0].keys()))
                names.reverse()
                for l in v:
                    pre=names.pop()
                    for ki,vi in l.items():
                        xcfg.set(k,"%s.%s" % (pre,ki),hvalue(vi))                        
        elif base is not None:
            if not xcfg.has_section(base):
                xcfg.add_section(base)
            xcfg.set(base,k,hvalue(v))

    # Writing our configuration file to 'example.cfg'
    with file(fname, 'wb') as configfile:
        xcfg.write(configfile)

 
def cfg2hash(filename,h=None,secure=False,klass=udict,includes=False,extra=False):
    """
    Read a configuration file into a configuration dictionary

    @param filename: name of the configuration file to read
    @type filename: unicode

    @param h: input dictionary (if any)
    @param h: dictionary

    @param secure: check if configuration file is secure
    @type secure: bool

    @param klass: class of input dictionary (default udict)
    @type klass: dictionary class (dict,udict,ldict)

    @raises: ConfigNotExistsError

    ::
      [section]
      active=yes | no
      kind = list | set
      list = a..., b...
      set =  a..., b....
      keys = akey, bkey ...

    """
    global _defines
    if filename[0]=='~':
        filename=expanduser(filename)
    if h is None:
        h=klass()
    def get_value(v):
        return v # Patch
        if re.match('^null$',v,re.IGNORECASE) or re.match('^none$',v,re.IGNORECASE):
		raise Exception('No Value')
	if re.match('^(true|false)$',v,re.IGNORECASE):
                if re.match('^true$',v,re.IGNORECASE):
			return True
                else:
			return False
	else:
                return v
    if not os.path.exists(filename):
        logger.error("Non posso leggere il file %s" % filename)
        raise ConfigNotExistsError(filename)
    if secure:
        statinfo = os.stat(filename)
        mode = statinfo[ST_MODE]
        if mode & S_IROTH:
            logger.error("Il file %s non ha le debite protezioni" % filename)
            logger.error("usa il comando: chmod 660 %s" % filename)
            logger.error("e poi riprova")
            raise ConfigNotProtectedError(filename)    
    
    cfg = ConfigParser(percent_expand=False,
                       dollar_expand=False,
                       case_sensitive=False,
                       section_case_sensitive=False,
                       inline_comments=False,
                       inherit_defaults=True,
                       safe_set=False,
                       encoding='utf8',
                       )

    if includes:
        fp = _get_temp_file_with_include(filename)
        cfg.readfp(fp,filename=filename)
    else:
        cfg.read(filename)
    secs = cfg.sections()
    for s in secs:
        lists=None
        fields=None
        if cfg.has_option(s,'active') and cfg.get(s,'active').lower()=='no':
            continue                    
        # if cfg.has_option(s,'sets'):
        #     R   = cfg.get(s,'sets').split(',')
        #     reg = R[0]
        #     fields = R[1:]
        #     lists = re.compile(reg)
        # elif cfg.has_option(s,'lists'):
        #     reg   = cfg.get(s,'lists')
        #     lists = re.compile(reg)
        # if cfg.has_option(s,'kind') and cfg.get(s,'kind').lower()=='list':
        #     h[s]=cfg.get(s,'list').split(',')
        #     continue
        # if cfg.has_option(s,'kind') and cfg.get(s,'kind').lower()=='set':
        #     elems = cfg.get(s,'set').split(',')
        #     keys = cfg.get(s,'keys').split(',')
        #     h[s]=[]
        #     for el in elems:
        #         m=klass()
        #         for ky in keys:
        #             try:
        #                 m[ky]=get_value(cfg.get(s,"%s.%s"%(el,ky)))
        #             except:
        #                 pass
        #         h[s].append(m)
        #     continue
        # nor list nor set
        h[s]=klass()
        if extra:
            h[s][u'__LABEL']=s
            h[s][u'__FILE']=filename
            h[s][u'__LOC']=0
        pkk = None
        IT = cfg.items(s)
        for k,v in IT:
            try:
                if lists is None:
                    _k=k
                    cond = None
                    if '|' in _k:
                        _k,cond = _k.split('|',1)
                    if extra:
                        h[s][u'__%s_LOC'%_k]=str(cfg.setting_location(s,k)[1])   
                        h[s][u'__LOC']=min(h[s][u'__%s_LOC'%_k],h[s][u'__LOC'])
                    kk=get_value(v)
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
                    if s=='PARAMS':
                        _defines[k]=kk
                    if cond:
                        if not h[s].has_key(_k):
                            h[s][_k] = []
                            h[s]["__%s_COND"%_k]=[]
                        h[s][_k].append(kk)
                        h[s]["__%s_COND"%_k].append(cond)
                    else:
                        h[s][_k]=kk
                else:
                    m = lists.match(k)
                    if m is not None:
                        if not h[s].has_key('list_elems'):
                            h[s]['list_elems']=[]
                        h[s]['list_elems'].append(k)
                        kk=v.split(',')
                        if fields is None:
                            h[s][k]=kk
                        else:
                            h[s][k]=dict(zip(fields,kk))                    
                    else:
                        h[s][k]=get_value(v)
            except Exception, exc:
                print exc
                pass
    return h

def cfg_exists_and_has_session(config_file,session,secure=True):
    """
    Return configuration dictionary from configuration file is session is present

    @param config_file: path of the configuration file
    @type config_file: unicode

    @param session: session name
    @type session: unicode

    @param secure: configuration file has to be secured
    @type secure: bool

    @returns: dictionary
    """

    logger.info('exists cfg %s and session %s',config_file,session)
    conf_file=expanduser(config_file) 
    if not os.path.exists(conf_file):
        raise ConfigNotExistsError()
    config = cfg2hash(conf_file,None,secure=secure)
    if session is not None:
        if config.has_key(session):
            pass
        else:
            raise NoSessionInConfigFileError, 'cfg %s and session %s exists'%(config_file,session)
    logger.info('cfg %s and session %s exists',config_file,session)
    return config

def get_session(config_file,session,**kwargs):
    """
    Return session in C{config_file}
    
    @param config_file: path of the configuration file
    @type config_file: unicode

    @param session: session name
    @type session: unicode

    @param secure: configuration file has to be secured
    @type secure: bool

    @returns: dictionary

    """
    logger.info('getting session from file %s',config_file)
    secure = False
    if kwargs.has_key('secure'):         
        secure = kwargs['secure']
        del kwargs['secure']

    config = cfg_exists_and_has_session(config_file,
                                         session,                                   
                                         secure=secure)
    info = {}
    cfg = config[session]
    for k,v in kwargs.items():
        if type(v)==type(list()):
            default = v[0]
            exc = v[1]
        else:
            default=v
            exc = None
        if not cfg.has_key(k):
            if default is not None:
                value = default
            elif exc is not None:
                raise exc(session)
            else:
                value = None
        else:
            value=cfg[k]
        info[k] = value
    return info


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

def get_intlist(collection, sep=',',limit=None):
    """
    Split the collection string in a list of ints by separator sep

    @param collection: string containing one or more element 
    @type collection: unicode
    
    @param sep: separator character (defaults to ',')
    @type sep: unicode

    @param limit: get only first C{limit} elements
    @type limit: int

    @returns: list of int elements 
    """
    if collection:
        return get_numlist(collection,sep,limit,int)

def get_numlist(collection, sep=',',limit=None,klass=int):
    """
    Split the collection string in a list of ints by separator sep

    @param collection: string containing one or more element 
    @type collection: unicode
    
    @param sep: separator character (defaults to ',')
    @type sep: unicode

    @param limit: get only first C{limit} elements
    @type limit: int

    @param klass: cast class for elements (defaults to int)
    @type klass: type or class 

    @returns: list of C{klass} elements 
    """
    if collection:
        if limit:
            return [ klass(el.strip()) 
                     for i,el in enumerate(collection.split(sep)) if i<limit ]
        return [ klass(el.strip()) for el in collection.split(sep) ]

def explode_list(values,elements=None):
	"""Return an exploded list if values has $$ in it"""
	val_list = get_list(values)
	if '$$' in values and elements is not None:
		if type(elements) in (list,tuple):
			elm_list = elements
		elif type(elements) in (str,unicode):
			elm_list = get_list(elements)
		else:
			raise SyntaxError, "type of elements in _explode_list"
		_glist = []
		for _p in elm_list:
			_glist.extend([ _v.replace('$$',_p) for _v in val_list ])
		return _glist
	return val_list

def extract_dict_from_key(keylist,_dict1,_dict2,_defaults,base=udict(),
                          klass=udict,retain_keys=False):
    """Get _dict2[_k for _k in _dict1[key]] if exists
    else if _dict1[key] is yes or no return {'ACTIVE': True/False, key: _dict1[key]}
    else {key: _dict1[key]} if can or
    else _defaults[key] 
    or None"""


    if isinstance(keylist,(tuple,list)):
        _keys = keylist
    elif isinstance(keylist,dict):
        _keys = keylist.keys()
    elif isinstance(keylist,basestring):
        _keys = get_list(keylist)
    else:
        raise ValueError, "extract_dict_from_key - type is %s" % type(keylist)

    logger.debug('{EXTRACT_DICT_FROM_KEY} keylist is %s: ',','.join(_keys))

    _ret = klass(base)

    for key in _keys:
        if retain_keys:
            _key = key
        else:
            _key = None

        if not _dict1.has_key(key):
            
            if _defaults and _defaults.has_key(key):
                _val = klass(_defaults[key])
                _ret.update(klass({_key:_val}) if _key else _val )
                continue

        if re.match('^(yes|on|true)$',_dict1[key],re.I):
            _val = klass({'ACTIVE': True, key: _dict1[key]})
            _ret.update(klass({_key:_val}) if _key else _val )
            continue

        if re.match('^(no|off|false)$',_dict1[key],re.I):
            _val = klass({'ACTIVE': False, key: _dict1[key]})
            _ret.update(klass({_key:_val}) if _key else _val )
            continue

        _lst = get_list(_dict1[key])
    
        for _l in _lst:
            if _dict2.has_key(_l):
                _val = klass(_dict2[_l])
                _ret.update(klass({_key:_val}) if _key else _val )
            else:
                _val = klass({key: _l})
                _ret.update(klass({_key:_val}) if _key else _val )

    logdict(logger.debug,'{EXTRACT_DICT_FROM_KEY} result',_ret)

    return _ret

class subsection(object):
    pass

def tuple_of_ints(instr,*args):
        m = re.match('^\(([0-9]+( *, *[0-9]+)+)\)$',instr)
        if m:
            int_list = get_intlist(m.group(1))
            return list(int_list)
					
def tuple_of_floats(instr,*args):
    m = re.match('^\(([0-9.]+,([0-9.]+)*)\)$',instr)
    if m:
        return list(get_numlist(m.group(1),klass=float))

def boolean(instr,*args):
    if isinstance(instr,bool): return instr
    if re.match('^yes|true|on|1$',instr,re.I): return True
    if re.match('^no|falese|off|0$',instr,re.I): return False
    raise ValueError, instr


def cast_dict(anInput,aCastDict,aOptsDict=None):
    if anInput is None:
        return None
    logger.debug('{CAST_DICT} anInput %s',anInput)
    logdict(logger.debug,'{CAST_DICT} aCast %s'%type(aCastDict),aCastDict)
    if isinstance(anInput,(dict,ldict,udict)):
        aList = (anInput,)
    elif isinstance(anInput,(list,tuple)):
        aList = anInput
    else:
        raise ValueError, "{CAST_DICT}"
    oList = []
    cd = udict(aCastDict)
    for aDict in aList:
        _res = {}        
        if aDict:
            for k,v in aDict.items():
                if cd.has_key(k):
                    spec = cd[k]
                    cast = spec
                    logger.debug('{CAST_DICT} loop %s %s | %s=%s',type(spec),type(subsection),k,v)
                    if isinstance(cast,tuple):
                        cast = spec[1]
                        spec = spec[0]
                        value = cast(spec(v))
                    elif cast==subsection:
                        value=None
                        if aOptsDict.has_key(v):
                            value = aOptsDict[v]
                        logger.debug('{CAST_DICT} SUBSECTION %s',value)
                    else:
                        # print cast
                        value = cast(v)
                    _res[k]=value
            logdict(logger.debug,'{CAST_DICT} aDict %s'%type(aDict),aDict)
            logdict(logger.debug,'{CAST DICT} rDict %s'%type(_res),_res)
        oList.append(_res)
    return oList

def read_conf_file(cfg="~/.srirc",section='SRI',opts={},options=Options()):
    """Legge il file di configurazione delle risorse del programma nelle opzioni"""
    _d = {}
    opts = udict(opts)
    rc = expandvars(expanduser(cfg))
    if exists(rc):
        _ch = cfg2hash(rc)
        if _ch.has_key(section):            
            _l = dict([ (k,v) for k,v in _ch[section].items() if k in opts.keys()])
            _l = [ ((("switch_%s" % k) if opts[k] is bool else k)  ,
                    expandvars(expanduser(v)) if opts[k] is str else eval(v))  
                   for k,v in _l.items() ]
            _d = dict(_l)
            if _d.has_key('define'):
                _d['define'] = _d['define'].split(',')

    for k,v in _d.items():
        setattr(options,k.lower(),v)
    return options

__all__ = """
 ConfigNotExistsError
 ConfigNotProtectedError
 ConfigNotProtectedDBError
 NoSessionInConfigFileError
 hash2cfg
 cfg2hash
 cfg_exists_and_has_session
 get_session
 get_list
 get_intlist
 get_numlist
 explode_list
 extract_dict_from_key
 tuple_of_ints
 tuple_of_floats
 boolean
 cast_dict
 ParseError
 MissingSectionHeaderError
 read_conf_file
""".split()
