#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from langconv import *

class ConvertMapTest(TestCase):
    def test_map(self):
        mapping = {'a': 'b', 'b': 'a', 'abc': 'cba', 'cb': 'bb'}
        cm = ConvertMap('test', mapping)
        self.assertEqual(len(cm), 6) # with switch node: 'ab' and 'c'
        self.failUnless('a' in cm)
        self.failUnless('c' in cm)
        self.failIf('bc' in cm)
        self.assertEqual(cm['a'].data, (True, True, 'b'))
        self.assertEqual(cm['b'].data, (True, False, 'a'))
        self.assertEqual(cm['c'].data, (False, True, ''))
        self.assertEqual(cm['ab'].data, (False, True, ''))
        self.assertEqual(cm['abc'].data, (True, False, 'cba'))
        self.assertEqual(cm['cb'].data, (True, False, 'bb'))

class ConverterModelTest(TestCase):
    def test_1(self):
        registery('rev', {'a': 'c', 'c': 'a'})
        c = Converter('rev')
        c.feed('a')
        self.assertEqual(c.get_result(), 'c')
        c.feed('b')
        self.assertEqual(c.get_result(), 'cb')
        c.feed('c')
        self.assertEqual(c.get_result(), 'cba')

    def test_2(self):
        registery('2', {'b': 'a', 'ab': 'ab'})
        c = Converter('2')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('b')
        self.assertEqual(c.get_result(), 'ab')

    def test_3(self):
        registery('3', {'a': 'b', 'ab': 'ba'})
        c = Converter('3')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('b')
        self.assertEqual(c.get_result(), 'ba')
        c.feed('a')
        self.assertEqual(c.get_result(), 'ba')
        c.feed('c')
        self.assertEqual(c.get_result(), 'babc')

    def test_4(self):
        registery('4', {'ab': 'ba'})
        c = Converter('4')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('b')
        self.assertEqual(c.get_result(), 'ba')
        c.feed('a')
        self.assertEqual(c.get_result(), 'ba')
        c.feed('c')
        self.assertEqual(c.get_result(), 'baac')

    def test_5(self):
        registery('5', {'ab': 'ba'})
        c = Converter('5')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('b')
        self.assertEqual(c.get_result(), 'aba')

    def test_6(self):
        registery('6', {'abc': 'cba'})
        c = Converter('6')
        c.feed('a')
        c.feed('b')
        self.assertEqual(c.get_result(), '')
        c.feed('c')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('a')
        c.feed('b')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('b')
        self.assertEqual(c.get_result(), 'cbaabb')

    def test_7(self):
        registery('7', {'abc': 'cba', 'bc': 'cb'})
        c = Converter('7')
        c.feed('a')
        c.feed('b')
        self.assertEqual(c.get_result(), '')
        c.feed('c')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('a')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('')
        self.assertEqual(c.get_result(), 'cbaa')

    def test_8(self):
        registery('8', {'abc': 'cba', 'ab': 'ba'})
        c = Converter('8')
        c.feed('a')
        c.feed('b')
        self.assertEqual(c.get_result(), '')
        c.feed('c')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('a')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('b')
        self.assertEqual(c.get_result(), 'cba')
        c.feed('b')
        self.assertEqual(c.get_result(), 'cbabab')

    def test_9(self):
        registery('9', {'bx': 'dx', 'c': 'e', 'cy': 'cy'})
        c = Converter('9')
        c.feed('a')
        self.assertEqual(c.get_result(), 'a')
        c.feed('b')
        self.assertEqual(c.get_result(), 'a')
        c.feed('c')
        self.assertEqual(c.get_result(), 'a')
        c.end()
        self.assertEqual(c.get_result(), 'abe')

    def test_10(self):
        registery('10', {'a': 'd', 'b': 'e', 'ab': 'cd', 'by': 'yy'})
        c = Converter('10')
        c.feed('a')
        self.assertEqual(c.get_result(), '')
        c.feed('b')
        self.assertEqual(c.get_result(), '')
        c.feed('c')
        c.end()
        self.assertEqual(c.get_result(), 'cdc')

class ConverterTest(TestCase):
    def assertConvert(self, name, string, converted):
        c = Converter(name)
        new = c.convert(string)
        assert new == converted, (
                "convert(%s, '%s') should return '%s' but '%s'" % (
                    repr(name), string, converted, new)).encode('utf8')

    def assertST(self, trad, simp):
        if not py3k:
            trad = trad.decode('utf-8')
            simp = simp.decode('utf-8')
        self.assertConvert('zh-hans', trad, simp)
        self.assertConvert('zh-hant', simp, trad)

    def test_zh1(self):
        self.assertST('乾燥', '干燥')
        self.assertST('乾坤', '乾坤')
        self.assertST('乾隆', '乾隆')
        self.assertST('幹事', '干事')
        self.assertST('牛肉乾', '牛肉干')
        self.assertST('相干', '相干')

    def test_zh2(self):
        self.assertST('印表機', '打印机')
        self.assertST('說明檔案', '帮助文件')

    def test_zh3(self):
        self.assertST('頭髮', '头发')
        self.assertST('頭髮和', '头发和')
        self.assertST('發生', '发生')
        self.assertST('頭髮和發生', '头发和发生')

    def test_zh4(self):
        self.assertST('著名', '著名')
        self.assertST('覆蓋', '覆盖')
        self.assertST('翻來覆去', '翻来覆去')
        self.assertST('獃獃', '呆呆')
        self.assertST('獃住', '呆住')
        self.assertST('壁畫', '壁画')
        self.assertST('畫面', '画面')
        self.assertST('顯著', '显著')
        self.assertST('土著人', '土著人')
        self.assertST('長春鹼', '长春碱')
        self.assertST('嘌呤鹼', '嘌呤碱')
        self.assertST('嘧啶鹼', '嘧啶碱')

if '__main__' == __name__:
    import unittest
    unittest.main()

