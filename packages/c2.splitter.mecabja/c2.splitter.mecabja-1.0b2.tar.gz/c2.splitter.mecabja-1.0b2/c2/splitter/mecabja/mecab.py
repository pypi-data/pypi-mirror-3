# -*- coding: utf-8 -*-
import unicodedata

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import MeCab

# arguments passed to mecab
NG_WORDS = ('*','?')
#REPLACE_WORDS = (('スペース',' '),)

enc = 'utf-8'

def get_wakati_only_part(txt, adaptor, part,):
    part_adaptor = adaptor
    if not isinstance(txt, str):
        txt = txt.encode(enc)
    words = part_adaptor.parse(txt).split('\n')
    for word in words:
        if word in ["EOS", ""]:
            continue
        try:
            w, info = word.split('\t')
        except:
            print "What :", repr(word)
        detail_info = info.split(',')
        detail_len = len(detail_info)
        main_part = detail_info[0]
        if detail_len > 8:
            prototype = detail_info[6]
            yomi = detail_info[7]
        elif detail_len > 6:
            prototype = w
            yomi = w
        else:
            prototype = w
            yomi = ""
        if main_part in part:
            yield prototype, yomi

class C2MeCabAdaptor(object):
    """
     wrapper of MeCab::Tagger
    """
    def __init__(self):
        self.adaptor = MeCab.Tagger('-Owakati')
        self.part_adaptor = MeCab.Tagger()

    def parse(self, txt):
        if not isinstance(txt, str):
            txt = txt.encode(enc)
        words = self.adaptor.parse(txt).split()
        return (w for w in words if w and w not in NG_WORDS)

    def wakati_part(self, txt, part=None):
        if part is None:
            part = ("名詞", "動詞")
        return get_wakati_only_part(txt, adaptor=self.part_adaptor, part=part)

#    def get_yomi(self, txt):
#        yomi_adaptor = MeCab.Tagger('-Oyomi')
#        if not isinstance(txt, str):
#            txt = txt.encode(enc)
#        sentence = yomi_adaptor.parse(txt)
#        return sentence

class C2MecabSplitter(object):
    """
    Mecab-based Japanese Splitter
    """
    __implements__ = ISplitter

    mecabAdaptor = C2MeCabAdaptor()

    def process(self, text, glob=0):
        txt = ' '.join(text)
        return self.mecabAdaptor.parse(txt)

element_factory.registerFactory('Word Splitter',
                        'C2MecabSplitter', C2MecabSplitter)

class C2MecabPartSplitter(object):
    """
    Mecab-based Japanese Splitter
    """
    __implements__ = ISplitter

    mecabAdaptor = C2MeCabAdaptor()

    def process(self, text, glob=0):
        if isinstance(text, basestring):
            txt = text
        else:
            txt = ' '.join(text)
        return (p for p, y in self.mecabAdaptor.wakati_part(txt) if p)

element_factory.registerFactory('Word Splitter',
    'C2MecabPartSplitter', C2MecabPartSplitter)

class C2MecabYomiSplitter(object):
    """
    Mecab-based Japanese Splitter
    """
    __implements__ = ISplitter

    mecabAdaptor = C2MeCabAdaptor()

    def process(self, text, glob=0):
        if isinstance(text, basestring):
            txt = text
        else:
            txt = ' '.join(text)
        return (y for p, y in self.mecabAdaptor.wakati_part(txt) if y)

element_factory.registerFactory('Word Splitter',
    'C2MecabYomiSplitter', C2MecabYomiSplitter)



class C2MecabNormalizer(object):

    def process(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the normalizer working with
            # non-unicode text.
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, enc)
            except (UnicodeDecodeError, TypeError):
                result.append(s.lower())
            else:
                normalized = unicodedata.normalize('NFKC', s)
                result.append(normalized.lower().encode(enc))
        return result

element_factory.registerFactory('Case Normalizer',
        'C2Mecab Case Normalizer', C2MecabNormalizer)
