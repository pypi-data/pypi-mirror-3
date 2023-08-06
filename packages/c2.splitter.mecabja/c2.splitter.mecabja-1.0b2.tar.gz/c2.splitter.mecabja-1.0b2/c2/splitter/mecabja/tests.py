# -*- coding: utf-8 -*-
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from Products.CMFCore.utils import getToolByName


ptc.setupPloneSite()

import c2.splitter.mecabja

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             c2.splitter.mecabja)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class TestCanUseSpritter(TestCase):
    """Can Replace the catalog """
    def afterSetUp(self):
        pass

    def testWordSplitter(self):
        from Products.ZCTextIndex.PipelineFactory import element_factory
        group = 'Word Splitter'
        names = element_factory.getFactoryNames(group)
        self.failUnless('C2MecabSplitter' in names)

        group = 'Case Normalizer'
        names = element_factory.getFactoryNames(group)
        self.failUnless('C2Mecab Case Normalizer' in names)


    def testNounSearchableText(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        # インデックスを作る
        from Products.ZCTextIndex.OkapiIndex import OkapiIndex
        from Products.ZCTextIndex.ZCTextIndex import PLexicon
        from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
        lexicon = PLexicon('c2mecab_lexicon', '', c2.splitter.mecabja.mecab.C2MecabNormalizer())
        cat._setObject('c2mecab_lexicon', lexicon)
        i = ZCTextIndex('NounSearchableText', caller=cat,
                index_factory=OkapiIndex,
                lexicon_id=lexicon.id)
        cat.addIndex('NounSearchableText', i)

        self.failUnless('NounSearchableText' in cat.indexes())
        self.failUnless('c2mecab_lexicon' in
                        [ix.getLexicon().id for ix in cat.index_objects()
                         if ix.id == 'NounSearchableText'])

class TestMecabFunctions(unittest.TestCase):
    """Test for Functions"""
    def afterSetUp(self):
        pass

    def test_get_wakati_yomi(self):
        get_wakati_only_part = c2.splitter.mecabja.mecab.get_wakati_only_part
        txt = "太郎はこの本を二郎を見た女性に渡した。"
        result = [("太郎", "タロウ"),
                  ("本", "ホン"),
                  ("二", "ニ"),
                  ("郎", "ロウ"),
                  ("見る", "ミ"),
                  ("女性", "ジョセイ"),
                  ("渡す", "ワタシ")]
        self.assertEqual(list(get_wakati_only_part(txt, part=["名詞", "動詞"])),
                        result)

def test_suite():
    return unittest.TestSuite([

        unittest.makeSuite(TestCanUseSpritter),
        unittest.makeSuite(TestMecabFunctions),
        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='c2.splitter.mecabja',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='c2.splitter.mecabja.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='c2.splitter.mecabja',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='c2.splitter.mecabja',
        #    test_class=TestCase),

        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
