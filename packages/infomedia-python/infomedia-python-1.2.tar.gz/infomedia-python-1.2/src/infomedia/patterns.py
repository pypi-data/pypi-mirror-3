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

# from http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
class Borg(object):
    _state = {}
    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._state
        return self

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


__all__ = """
 Borg
 Singleton
""".split()
