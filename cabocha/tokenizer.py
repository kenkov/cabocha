#! /usr/bin/env python
# coding:utf-8


from cabocha.analyzer import CaboChaAnalyzer


class CaboChaBasicTokenizer:
    """CaboCha による原型トークナイザ。
    pos がセットされた場合は、pos であるトークンに制限する"""
    def __init__(self, pos=None):
        self._analyzer = CaboChaAnalyzer()
        self._pos = pos

    def tokenize(self, text):
        if self._pos:
            return [token.surface if token.genkei == "*" else token.genkei
                    for token in self._analyzer.parse(text).tokens
                    if token.pos in self._pos]
        else:
            return [token.surface if token.genkei == "*" else token.genkei
                    for token in self._analyzer.parse(text).tokens]
