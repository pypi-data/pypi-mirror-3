### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" IP network field
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

import re
from interfaces import IIPNetwork 
from zope.interface import implements
from zope.schema import Field
from zope.schema._bootstrapinterfaces import InvalidValue

class IPNetwork(Field):
    """ IP address field """
    implements(IIPNetwork)
    _type = (str, unicode)
    
    _pattern = "^(\d+)(?:\.(\d+)(?:\.(\d+)(?:\.(\d+))?)?)?/(\d+)$" 
    
    def _validate(self, value):
        """ checks the value given """
        super(IPNetwork, self)._validate(value)
        _parts = re.findall(self._pattern, value.strip())
        if not _parts : raise InvalidValue(value)
        parts = map(int, filter(None,_parts[0]))
        net = parts[:-1]
        mask = parts[-1]
        if mask > 32 : raise InvalidValue(value)
        for i in net:
            if i > 255 : raise InvalidValue(value)
            
    def set(self, object, value):
        """ sets the value """
        _parts = re.findall(self._pattern, value.strip())
        parts = map(int, filter(None,_parts[0]))
        net = parts[:-1]
        mask = parts[-1]
        net = ".".join(map(str,net))
        v = "%s/%s" % (net, mask)
        super(IPNetwork, self).set(object, v)