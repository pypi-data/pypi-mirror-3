# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Jim Washington and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""JSON Tests
jwashin 2005-08-18
"""
import unittest

from Products.jsonserver import minjson as json
from Products.jsonserver.minjson import ReadException

def spaceless(aString):
    return aString.replace(' ','')

class JSONTests(unittest.TestCase):

    def testReadString(self):
        s = u"'hello'"
        self.assertEqual(json.read(s) ,'hello')

    def testWriteString(self):
        s = 'hello'
        self.assertEqual(json.write(s), '"hello"')

    def testReadInt(self):
        s = u"1"
        self.assertEqual(json.read(s), 1)

    def testWriteInt(self):
        s = 1
        self.assertEqual(json.write(s), "1")

    def testReadLong(self):
        s = u"999999999999999999999"
        self.assertEqual(json.read(s), 999999999999999999999)

    def testWriteShortLong(self):
        s = 1L
        self.assertEqual(json.write(s), "1")

    def testWriteLongLong(self):
        s = 999999999999999999999L
        self.assertEqual(json.write(s), "999999999999999999999")

    def testReadNegInt(self):
        s = u"-1"
        self.assertEqual(json.read(s), -1)

    def testWriteNegInt(self):
        s = -1
        self.assertEqual(json.write(s), '-1')

    def testReadFloat(self):
        s = u"1.334"
        self.assertEqual(json.read(s), 1.334)

    def testReadEFloat1(self):
        s = u"1.334E2"
        self.assertEqual(json.read(s), 133.4)

    def testReadEFloat2(self):
        s = u"1.334E-02"
        self.assertEqual(json.read(s), 0.01334)

    def testReadeFloat1(self):
        s = u"1.334e2"
        self.assertEqual(json.read(s), 133.4)

    def testReadeFloat2(self):
        s = u"1.334e-02"
        self.assertEqual(json.read(s), 0.01334)

    def testWriteFloat(self):
        s = 1.334
        self.assertEqual(json.write(s), "1.334")

    def testWriteDecimal(self):
        try:
            from decimal import Decimal
            s = Decimal('1.33')
            self.assertEqual(json.write(s), "1.33")
        except ImportError:
            pass

    def testReadNegFloat(self):
        s = u"-1.334"
        self.assertEqual(json.read(s), -1.334)

    def testWriteNegFloat(self):
        s = -1.334
        self.assertEqual(json.write(s), "-1.334")

    def testReadEmptyDict(self):
        s = u"{}"
        self.assertEqual(json.read(s), {})

    def testWriteEmptyList(self):
        s = []
        self.assertEqual(json.write(s), "[]")

    def testWriteEmptyTuple(self):
        s = ()
        self.assertEqual(json.write(s), "[]")

    def testReadEmptyList(self):
        s = u"[]"
        self.assertEqual(json.read(s), [])

    def testWriteEmptyDict(self):
        s = {}
        self.assertEqual(json.write(s), '{}')

    def testReadTrue(self):
        s = u"true"
        self.assertEqual(json.read(s), True)

    def testWriteTrue(self):
        s = True
        self.assertEqual(json.write(s), "true")

    def testReadStringTrue(self):
        s = u'"true"'
        self.assertEqual(json.read(s), 'true')

    def testWriteStringTrue(self):
        s = "True"
        self.assertEqual(json.write(s), '"True"')

    def testReadStringNull(self):
        s = u'"null"'
        self.assertEqual(json.read(s), 'null')

    def testWriteStringNone(self):
        s = "None"
        self.assertEqual(json.write(s), '"None"')

    def testReadFalse(self):
        s = u"false"
        self.assertEqual(json.read(s), False)

    def testWriteFalse(self):
        s = False
        self.assertEqual(json.write(s), 'false')

    def testReadNull(self):
        s = u"null"
        self.assertEqual(json.read(s), None)

    def testWriteNone(self):
        s = None
        self.assertEqual(json.write(s), "null")

    def testReadDictOfLists(self):
        s = u"{'a':[],'b':[]}"
        self.assertEqual(json.read(s), {'a':[],'b':[]})

    def testReadDictOfListsWithSpaces(self):
        s = u"{  'a' :    [],  'b'  : []  }    "
        self.assertEqual(json.read(s), {'a':[],'b':[]})

    def testWriteDictOfLists(self):
        s = {'a':[],'b':[]}
        self.assertEqual(spaceless(json.write(s)), '{"a":[],"b":[]}')

    def testWriteDictOfTuples(self):
        s = {'a':(),'b':()}
        self.assertEqual(spaceless(json.write(s)), '{"a":[],"b":[]}')

    def testWriteDictWithNonemptyTuples(self):
        s = {'a':('fred',7),'b':('mary',1.234)}
        w = json.write(s)
        self.assertEqual(spaceless(w), '{"a":["fred",7],"b":["mary",1.234]}')

    def testWriteVirtualTuple(self):
        s = 4,4,5,6
        w = json.write(s)
        self.assertEqual(spaceless(w), '[4,4,5,6]')

    def testReadListOfDicts(self):
        s = u"[{},{}]"
        self.assertEqual(json.read(s), [{},{}])

    def testReadListOfDictsWithSpaces(self):
        s = u" [ {    } ,{   \n} ]   "
        self.assertEqual(json.read(s), [{},{}])

    def testWriteListOfDicts(self):
        s = [{},{}]
        self.assertEqual(spaceless(json.write(s)), "[{},{}]")

    def testWriteTupleOfDicts(self):
        s = ({},{})
        self.assertEqual(spaceless(json.write(s)), "[{},{}]")

    def testReadListOfStrings(self):
        s = u"['a','b','c']"
        self.assertEqual(json.read(s), ['a','b','c'])

    def testReadListOfStringsWithSpaces(self):
        s = u" ['a'    ,'b'  ,\n  'c']  "
        self.assertEqual(json.read(s), ['a','b','c'])

    def testReadStringWithWhiteSpace(self):
        s = ur"'hello \tworld'"
        self.assertEqual(json.read(s), 'hello \tworld')

    def testWriteMixedList(self):
        o = ['OIL',34,199L,38.5]
        self.assertEqual(spaceless(json.write(o)), '["OIL",34,199,38.5]')

    def testWriteMixedTuple(self):
        o = ('OIL',34,199L,38.5)
        self.assertEqual(spaceless(json.write(o)), '["OIL",34,199,38.5]')

    def testWriteStringWithWhiteSpace(self):
        s = 'hello \tworld'
        self.assertEqual(json.write(s), r'"hello \tworld"')

    def testWriteListofStringsWithApostrophes(self):
        s = ["hasn't","don't","isn't",True,"won't"]
        w = json.write(s)
        self.assertEqual(spaceless(w), '["hasn\'t","don\'t","isn\'t",true,"won\'t"]')

    def testWriteTupleofStringsWithApostrophes(self):
        s = ("hasn't","don't","isn't",True,"won't")
        w = json.write(s)
        self.assertEqual(spaceless(w), '["hasn\'t","don\'t","isn\'t",true,"won\'t"]')

    def testWriteListofStringsWithRandomQuoting(self):
        s = ["hasn't","do\"n't","isn't",True,"wo\"n't"]
        w = json.write(s)
        assert "true" in w

    def testWriteStringWithDoubleQuote(self):
        s = "do\"nt"
        w = json.write(s)
        self.assertEqual(w, '"do\\\"nt"')

    def testReadDictWithSlashStarComments(self):
        s = """
        {'a':false,  /*don't want b
            b:true, */
        'c':true
        }
        """
        self.assertEqual(json.read(s), {'a':False,'c':True})

    def testReadDictWithTwoSlashStarComments(self):
        s = """
        {'a':false,  /*don't want b
            b:true, */
        'c':true,
        'd':false,  /*don;t want e
            e:true, */
        'f':true
        }
        """
        self.assertEqual(json.read(s), {'a':False,'c':True, 'd':False,'f':True})

    def testReadDictWithDoubleSlashComments(self):
        s = """
        {'a':false,
          //  b:true, don't want b
        'c':true
        }
        """
        self.assertEqual(json.read(s), {'a':False,'c':True})

    def testReadStringWithEscapedSingleQuote(self):
        s = '"don\'t tread on me."'
        self.assertEqual(json.read(s), "don't tread on me.")

    def testWriteStringWithEscapedDoubleQuote(self):
        s = 'he said, \"hi.'
        t = json.write(s)
        self.assertEqual(t, '"he said, \\\"hi."')

    def testReadStringWithEscapedDoubleQuote(self):
        s = r'"She said, \"Hi.\""'
        self.assertEqual(json.read(s), 'She said, "Hi."')

    def testReadStringWithNewLine(self):
        s = r'"She said, \"Hi,\"\n to which he did not reply."'
        self.assertEqual(json.read(s), 'She said, "Hi,"\n to which he did not reply.')

    def testReadNewLine(self):
        s = r'"\n"'
        self.assertEqual(json.read(s), '\n')

    def testWriteNewLine(self):
        s = u'\n'
        self.assertEqual(json.write(s), r'"\n"')

    def testWriteSimpleUnicode(self):
        s = u'hello'
        self.assertEqual(json.write(s), '"hello"')

    def testReadBackSlashuUnicode(self):
        s = u'"\u0066"'
        self.assertEqual(json.read(s), 'f')

    def testReadBackSlashuUnicodeInDictKey(self):
        s = u'{"\u0066ather":34}'
        self.assertEqual(json.read(s), {'father':34})

    def testReadDictKeyWithBackSlash(self):
        s = u'{"mo\\use":22}'
        self.assertEqual(json.read(s), {r'mo\use':22})

    def testWriteDictKeyWithBackSlash(self):
        s = {"mo\\use":22}
        self.assertEqual(json.write(s), r'{"mo\\use":22}')
        #self.assertEqual(json.write(s), r'{"mo\\use": 22}')

    def testWriteListOfBackSlashuUnicodeStrings(self):
        s = [u'\u20ac',u'\u20ac',u'\u20ac']
        self.assertEqual(spaceless(json.write(s)), u'["\u20ac","\u20ac","\u20ac"]')

    def testWriteEscapedHexCharacter(self):
        s = json.write(u'\u1001')
        self.assertEqual(u'"\u1001"', s)

    def testWriteHexUnicode(self):
        s = unicode('\xff\xfe\xbf\x00Q\x00u\x00\xe9\x00 \x00p\x00a\x00s\x00a\x00?\x00','utf-16')
        self.assertEqual(json.write(s), u'"¿Qué pasa?"')

    def testWriteDosPath(self):
        s = 'c:\\windows\\system'
        self.assertEqual(json.write(s), r'"c:\\windows\\system"')

    def testWriteDosPathInList(self):
        s = ['c:\windows\system','c:\\windows\\system',r'c:\windows\system']
        #self.assertEqual(json.write(s), r'["c:\\windows\\system", "c:\\windows\\system", "c:\\windows\\system"]')
        self.assertEqual(json.write(s), r'["c:\\windows\\system","c:\\windows\\system","c:\\windows\\system"]')

    def readImportExploit(self):
        s = ur"\u000aimport('os').listdir('.')"
        json.read(s)

    def testImportExploit(self):
        self.assertRaises(ReadException, self.readImportExploit)

    def readClassExploit(self):
        s = ur'''"__main__".__class__.__subclasses__()'''
        json.read(s)

    def testReadClassExploit(self):
        self.assertRaises(ReadException, self.readClassExploit)

    def readBadJson(self):
        s = "'DOS'*30"
        json.read(s)

    def testReadBadJson(self):
        self.assertRaises(ReadException, self.readBadJson)

    def readUBadJson(self):
        s = ur"\u0027DOS\u0027*30"
        json.read(s)

    def testReadUBadJson(self):
        self.assertRaises(ReadException, self.readUBadJson)

    def testReadEncodedUnicode(self):
        obj = "'La Peña'"
        r = json.read(obj, 'utf-8')
        self.assertEqual(r, unicode('La Peña','utf-8'))

    def testUnicodeFromNonUnicode(self):
        obj = "'\u20ac'"
        r = json.read(obj)
        self.assertEqual(r, u'\u20ac')

    def testUnicodeInObjectFromNonUnicode(self):
        obj = "['\u20ac', '\u20acCESS', 'my\u20ACCESS']"
        r = json.read(obj)
        self.assertEqual(r, [u'\u20AC', u'\u20acCESS', u'my\u20acCESS'])

    def testWriteWithEncoding(self):
        obj = u"'La Peña'".encode('latin-1')
        r = json.write(obj, 'latin-1')
        self.assertEqual(r, '"%s"' % obj.decode('latin-1'))

    def testWriteWithEncodingBaseCases(self):
        input_uni =  u"Árvíztűrő tükörfúrógép"
        #input_uni = u'\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p'
        good_result = u'"\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p"'
        #
        # from utf8
        obj = input_uni.encode('utf-8')
        r = json.write(obj, 'utf-8')
        self.assertEqual(r, good_result)
        #
        # from unicode
        obj = input_uni
        r = json.write(obj)
        self.assertEqual(r, good_result)
        #
        # from latin2
        obj = input_uni.encode('latin2')
        r = json.write(obj, 'latin2')
        self.assertEqual(r, good_result)
        #
        # from unicode, encoding is ignored
        obj = input_uni
        r = json.write(obj, 'latin2')
        self.assertEqual(r, good_result)
        #
        # same with composite types, uni
        good_composite_result = \
        u'["\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p","\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p"]'
        #good_composite_result = \
        #u'["\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p", "\xc1rv\xedzt\u0171r\u0151 t\xfck\xf6rf\xfar\xf3g\xe9p"]'
        obj = [input_uni, input_uni]
        r = json.write(obj)
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, utf-8
        obj = [input_uni.encode('utf-8'), input_uni.encode('utf-8')]
        r = json.write(obj, 'utf-8')
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, latin2
        obj = [input_uni.encode('latin2'), input_uni.encode('latin2')]
        r = json.write(obj, 'latin2')
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, mixed utf-8 with unicode
        obj = [input_uni, input_uni.encode('utf-8')]
        r = json.write(obj, 'utf-8')
        self.assertEqual(r, good_composite_result)
        #
        # XXX The usage of site default encoding

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(JSONTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
