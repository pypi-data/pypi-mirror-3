### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" IP address field
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import re
from interfaces import IIPAddress 
from zope.interface import implements
from zope.schema import Field
from zope.schema._bootstrapinterfaces import InvalidValue

class IPAddress(Field):
    """ IP address field """
    implements(IIPAddress)
    _type = (str, unicode)
    _pattern = "^(\d+)\.(\d+)\.(\d+)\.(\d+)$"
    
    def _validate(self, value):
        """ checks the value given """
        super(IPAddress, self)._validate(value)
        _parts = re.findall(self._pattern, value.strip())
        if not _parts : raise InvalidValue(value)
        parts = map(int, _parts[0])
        if len(parts) != 4 : raise InvalidValue(value)
        for i in parts:
            if i > 255 : raise InvalidValue(value)
            
    def set(self, object, value):
        """ sets the value """
        _parts = re.findall(self._pattern, value.strip())
        parts = map(int, _parts[0])
        v = ".".join(map(str, parts))
        super(IPAddress, self).set(object, v)