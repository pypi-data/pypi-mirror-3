### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for IP network field
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

from sterch.fields.ip import IPNetwork
from unittest import main, makeSuite
from zope.schema import Int
from zope.schema.interfaces import RequiredMissing, InvalidValue, WrongType
from zope.schema.tests.test_field import FieldTestBase

class IPNetworkTest(FieldTestBase):
    """Test the Int Field."""

    _Field_Factory = IPNetwork

    def testValidate(self):
        field = self._Field_Factory(title=u'IP network field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate(u"10/8")
        field.validate(u"192.168/16")
        field.validate("127.0.0/24")
        field.validate(u"255.255.255.255/32")

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'IP network field', description=u'',
                                    readonly=False, required=True)
        field.validate(u"10/8")
        field.validate(u"192.168/16")
        field.validate("127.0.0/24")
        field.validate(u"255.255.255.255/32")

        self.assertRaises(RequiredMissing, field.validate, None)
        
    def testValidateTuple(self):
        field = self._Field_Factory(title=u'IP network field', description=u'',
                                    readonly=False, required=False)
        
        field.validate("255.255.255.255/32")
        self.assertRaises(InvalidValue, field.validate, "255.255.255.")
        self.assertRaises(InvalidValue, field.validate, "255.255.255./32")
        self.assertRaises(InvalidValue, field.validate, "255.255./32")
        self.assertRaises(InvalidValue, field.validate, "255./32")
        self.assertRaises(InvalidValue, field.validate, "./32")
        self.assertRaises(InvalidValue, field.validate, "..../32")
        self.assertRaises(InvalidValue, field.validate, ".1.1.1/32")
        self.assertRaises(InvalidValue, field.validate, ".1.1/32")
        self.assertRaises(InvalidValue, field.validate, ".1/32")
        self.assertRaises(InvalidValue, field.validate, "./32")
        self.assertRaises(InvalidValue, field.validate, "/32")
        self.assertRaises(InvalidValue, field.validate, "32")
        self.assertRaises(InvalidValue, field.validate, "a.a.a.a/32")
        self.assertRaises(InvalidValue, field.validate, "127.a.a.a/32")
        self.assertRaises(InvalidValue, field.validate, "127.127.a.a/32")
        self.assertRaises(InvalidValue, field.validate, "127.127.127.a/32")
        self.assertRaises(InvalidValue, field.validate, "127.127.a.127/32")
        self.assertRaises(InvalidValue, field.validate, "127.a.127.127/32")
        self.assertRaises(InvalidValue, field.validate, "a.127.127.127/32")
        self.assertRaises(InvalidValue, field.validate, "127...127/32")
        self.assertRaises(InvalidValue, field.validate, "127..127.127/32")
        self.assertRaises(InvalidValue, field.validate, "127.127.127.127/")
        self.assertRaises(InvalidValue, field.validate, "127.127.127.127/a")
        self.assertRaises(WrongType, field.validate, object())
        
    def testValidateNetwork(self):
        field = self._Field_Factory(title=u'IP network field', description=u'',
                                    readonly=False, required=False)
        
        field.validate("255.255.255.255/32")
        self.assertRaises(InvalidValue, field.validate, "127.0.0.-1/32")
        self.assertRaises(InvalidValue, field.validate, "127.0.-1.0/32")
        self.assertRaises(InvalidValue, field.validate, "127.-1.0.0/32")
        self.assertRaises(InvalidValue, field.validate, "-1.127.0.0/32")
        self.assertRaises(InvalidValue, field.validate, "256.127.0.0/32")
        self.assertRaises(InvalidValue, field.validate, "127.256.0.0/32")
        self.assertRaises(InvalidValue, field.validate, "127.0.256.0/32")
        self.assertRaises(InvalidValue, field.validate, "127.0.0.256/32")
        
    def testValidateMask(self):
        field = self._Field_Factory(title=u'IP network field', description=u'',
                                    readonly=False, required=False)
        
        field.validate("255.255.255.255/32")
        self.assertRaises(InvalidValue, field.validate, "255.255.255.255/33")
        self.assertRaises(InvalidValue, field.validate, "255.255.255.255/-1")
        self.assertRaises(InvalidValue, field.validate, "255.255.255.255/+1")
        
    def testSetGet(self):
        class Net(object): ip = None
        obj = Net()
        field = self._Field_Factory(__name__ = "ip",
                                    title=u'IP network field', description=u'')
        sample = {
            "10.0.0.10/32" : "10.0.0.10/32",
            "10.0.0.010/32" : "10.0.0.10/32",
            "10.0.00.10/32" : "10.0.0.10/32",
            "10.00.0.10/32" : "10.0.0.10/32",
            "010.0.0.10/32" : "10.0.0.10/32",
            "10.0.0.10/032" : "10.0.0.10/32",
            "010.00.00.010/032" : "10.0.0.10/32",          
            "\n 10.0.0.10/32 \r" : "10.0.0.10/32",
        }
        for k,v in sample.items():
            field.set(obj, k)
            self.assertEquals(field.get(obj),v)

        
                    
def test_suite():
    suite = makeSuite(IPNetworkTest)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
