### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Interfaces of the fields
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

from zope.schema.interfaces import IField

class IIPAddress(IField):
    """ Field to store IP addresses """
    
class IIPNetwork(IField):
    """ Field to store IP netword in the format a.b.c.d/mask, a/mask, a.b/mask etc. """