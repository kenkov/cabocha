#! /usr/bin/env python
# coding: utf-8


class Pred:

    def __init__(self, tree, chunk_id, token_id):
        self.tree = tree
        self.chunk_id = chunk_id
        self.token_id = token_id
        self.chunk = self.tree.chunks[self.chunk_id]
        self.token = self.tree.tokens[self.token_id]
        self.head = self.get_head_surface()
        self.normalized_surface = self.get_normalized_surface()
        self.kaku_structure = self.get_kaku_structure()
        self.types = self.get_types()

    def get_head_surface(self):
        tokens = self.chunk.get_tokens(end=self.token_id)
        return "".join(tk.surface for tk in tokens)

    def get_normalized_surface(self):
        pred_surface = "{}{}".format(
            self.head,
            self.token.genkei
        )
        return pred_surface

    def get_kaku_structure(self):
        kakus = self.get_kaku(self.chunk)
        kakus['pred'] = self.normalized_surface
        return kakus

    def get_kaku(self, chunk):
        dic = dict()
        for prev_chunk in chunk.prev_links:
            for key, val in self._get_kaku(prev_chunk).items():
                dic[key] = val

        return dic

    def _get_kaku(self, chunk):
        if all((token.pos in {'名詞'} for token in chunk)):
            return {'?': ''.join((token.surface for token in chunk))}
        tokens = []
        for token in chunk:
            if token.pos1 == '格助詞' or token.surface == 'は' and token.pos1 == '係助詞':
                dic = {token.surface: ''.join((tk.surface for tk in tokens))}
                return dic
            tokens.append(token)

        return dict()

    def get_types(self):
        _is_past_chunk = self._is_past_chunk(self.chunk)
        _is_negative_chunk = self._is_negative_chunk(self.chunk)
        flags = set()
        if _is_past_chunk:
            flags.add('p')
        if _is_negative_chunk:
            flags.add('n')
        return flags

    def _is_past_chunk(self, chunk):
        for token in chunk:
            if self._is_past_token(token):
                return True

        return False

    def _is_negative_chunk(self, chunk):
        chunk_str = ''.join((tk.surface for tk in chunk))
        if 'ません' in chunk_str:
            return True
        for token in chunk:
            if self._is_negative_token(token):
                return True

        return False

    def _is_past_token(self, token):
        return token.feature_list[4] == '特殊・タ'

    def _is_negative_token(self, token):
        if token.feature_list[4] == '特殊・ナイ':
            return True


if __name__ == '__main__':
    import sys
    from cabocha import CaboChaAnalyzer

    cabocha = CaboChaAnalyzer()

    for line in sys.stdin:
        text = line.strip('\n')
        tree = cabocha.parse(text)
        for pred in tree.find_preds():
            print(pred.kaku_structure)
            print(pred.types)
