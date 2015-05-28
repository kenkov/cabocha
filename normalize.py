#! /usr/bin/env python
# coding:utf-8

from cabocha import CaboChaAnalyzer


class Normalizer:
    def __init__(self):
        self.cabocha = CaboChaAnalyzer()
        self.dic = dict([
            ('a', 'ａ'), ('b', 'ｂ'), ('c', 'ｃ'), ('d', 'ｄ'), ('d', 'ｄ'),
            ('f', 'ｆ'), ('g', 'ｇ'), ('h', 'ｈ'), ('i', 'ｉ'), ('j', 'ｊ'),
            ('k', 'ｋ'), ('l', 'ｌ'), ('m', 'ｍ'), ('n', 'ｎ'), ('o', 'ｏ'),
            ('p', 'ｐ'), ('q', 'ｑ'), ('r', 'ｒ'), ('s', 'ｓ'), ('t', 'ｔ'),
            ('u', 'ｕ'), ('v', 'ｖ'), ('w', 'ｗ'), ('x', 'ｘ'), ('y', 'ｙ'),
            ('z', 'ｚ'),
            ('A', 'Ａ'), ('B', 'Ｂ'), ('C', 'Ｃ'), ('D', 'Ｄ'), ('D', 'Ｄ'),
            ('F', 'Ｆ'), ('G', 'Ｇ'), ('H', 'Ｈ'), ('I', 'Ｉ'), ('J', 'Ｊ'),
            ('K', 'Ｋ'), ('L', 'Ｌ'), ('M', 'Ｍ'), ('N', 'Ｎ'), ('O', 'Ｏ'),
            ('P', 'Ｐ'), ('Q', 'Ｑ'), ('R', 'Ｒ'), ('S', 'Ｓ'), ('T', 'Ｔ'),
            ('U', 'Ｕ'), ('V', 'Ｖ'), ('W', 'Ｗ'), ('X', 'Ｘ'), ('Y', 'Ｙ'),
            ('Z', 'Ｚ'),
            ('1', '１'), ('2', '２'), ('3', '３'), ('4', '４'), ('5', '５'),
            ('6', '６'), ('7', '７'), ('8', '８'), ('9', '９'), ('0', '０'),
        ])

    def half2full(self, text):
        ret = []
        for w in text:
            ret.append(self.dic[w] if w in self.dic else w)
        return "".join(ret)

    def normalize(self, text: str):
        tree = self.cabocha.parse(text)
        lst = []
        for chunk in tree:
            lst.extend([token.normalized_surface for token in chunk])
        txt = "".join(lst)
        return self.half2full(txt)


if __name__ == '__main__':
    import sys

    fd = open(sys.argv[1]) if len(sys.argv) >= 2 else sys.stdin
    norm = Normalizer()

    for text in (_.strip() for _ in fd):
        print(norm.normalize(text))
