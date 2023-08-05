### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Tests for IP address field
"""
__author__  = "Maxim Polscha (maxp@sterch.net)"
__license__ = "ZPL" 

from sterch.fields.ip import IPAddress
from unittest import main, makeSuite
from zope.schema import Int
from zope.schema.interfaces import RequiredMissing, InvalidValue, WrongType
from zope.schema.tests.test_field import FieldTestBase

class IPAddressTest(FieldTestBase):
    """Test the Int Field."""

    _Field_Factory = IPAddress

    def testValidate(self):
        field = self._Field_Factory(title=u'IP address field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate("10.0.0.10")
        field.validate("127.0.0.1")
        field.validate(u"0.0.0.0")
        field.validate(u"255.255.255.255")

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'IP address field', description=u'',
                                    readonly=False, required=True)
        field.validate("10.0.0.10")
        field.validate("127.0.0.1")
        field.validate(u"0.0.0.0")
        field.validate(u"255.255.255.255")

        self.assertRaises(RequiredMissing, field.validate, None)
        
    def testValidateTuple(self):
        field = self._Field_Factory(title=u'IP address field', description=u'',
                                    readonly=False, required=False)
        
        field.validate("255.255.255.255")
        self.assertRaises(InvalidValue, field.validate, "255.255.255.")
        self.assertRaises(InvalidValue, field.validate, ".255.255.255.255")
        self.assertRaises(InvalidValue, field.validate, "255.255.255")
        self.assertRaises(InvalidValue, field.validate, "255.255.")
        self.assertRaises(InvalidValue, field.validate, "255.255")
        self.assertRaises(InvalidValue, field.validate, "255.")
        self.assertRaises(InvalidValue, field.validate, "255")
        self.assertRaises(InvalidValue, field.validate, "")
        self.assertRaises(WrongType, field.validate, object())
        self.assertRaises(InvalidValue, field.validate, "a.a.a.a")
        self.assertRaises(InvalidValue, field.validate, "127.a.a.a")
        self.assertRaises(InvalidValue, field.validate, "127.127.a.a")
        self.assertRaises(InvalidValue, field.validate, "127.127.127.a")
        self.assertRaises(InvalidValue, field.validate, "127.127.a.127")
        self.assertRaises(InvalidValue, field.validate, "127.a.127.127")
        self.assertRaises(InvalidValue, field.validate, "a.127.127.127")
        self.assertRaises(InvalidValue, field.validate, "127...127")
        self.assertRaises(InvalidValue, field.validate, "127..127.127")
        
    def testValidateItem(self):
        field = self._Field_Factory(title=u'IP address field', description=u'',
                                    readonly=False, required=False)
        
        field.validate("255.255.255.255")
        self.assertRaises(InvalidValue, field.validate, "127.0.0.-1")
        self.assertRaises(InvalidValue, field.validate, "127.0.-1.0")
        self.assertRaises(InvalidValue, field.validate, "127.-1.0.0")
        self.assertRaises(InvalidValue, field.validate, "-1.127.0.0")
        self.assertRaises(InvalidValue, field.validate, "256.127.0.0")
        self.assertRaises(InvalidValue, field.validate, "127.256.0.0")
        self.assertRaises(InvalidValue, field.validate, "127.0.256.0")
        self.assertRaises(InvalidValue, field.validate, "127.0.0.256")

    def testSetGet(self):
        class Addr(object): ip = None
        obj = Addr()
        field = self._Field_Factory(__name__ = "ip",
                                    title=u'IP address field', description=u'')
        sample = {
            "10.0.0.10" : "10.0.0.10",
            "10.0.0.010" : "10.0.0.10",
            "10.0.00.10" : "10.0.0.10",
            "10.00.0.10" : "10.0.0.10",
            "010.0.0.10" : "10.0.0.10",
            "\n 10.0.0.10 \r" : "10.0.0.10",
        }
        for k,v in sample.items():
            field.set(obj, k)
            self.assertEquals(field.get(obj),v)
                   
def test_suite():
    suite = makeSuite(IPAddressTest)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
