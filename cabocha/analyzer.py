#! /usr/bin/env python
# coding:utf-8

import CaboCha
from collections import defaultdict
import cabocha.filter


class CaboChaAnalyzer:
    def __init__(self, *args, parser=CaboCha.Parser):
        self.parser = parser(*args)

    def analyze(self, text):
        return self.parse(text)

    def parse(self, text):
        tree = self.parser.parse(text)

        chunks = []
        tokens = []
        prev_links_dic = defaultdict(list)
        for chunk_pos in range(tree.chunk_size()):
            chunk_tokens = []
            chunk = tree.chunk(chunk_pos)
            for j in range(chunk.token_size):
                token_id = chunk.token_pos + j
                token = tree.token(token_id)
                mytoken = Token(
                    token_id,
                    token.additional_info,
                    token.feature,
                    [token.feature_list(i) for i in
                     range(token.feature_list_size)],
                    token.feature_list_size,
                    token.ne,
                    token.normalized_surface,
                    token.surface,
                )
                chunk_tokens.append(mytoken)
                tokens.append(mytoken)
            mychunk = Chunk(
                chunk_pos,
                chunk.additional_info,
                [chunk.feature_list(i)
                 for i in range(chunk.feature_list_size)],
                chunk.feature_list_size,
                chunk.func_pos,
                chunk.head_pos,
                chunk.link,
                chunk.score,
                chunk.token_pos,
                chunk.token_size,
                chunk_tokens
            )
            chunks.append(mychunk)

            if chunk.link >= 0:
                prev_links_dic[chunk.link].append(chunk_pos)

        for i, chunk in enumerate(chunks):
            chunks[i].set_links(prev_links_dic[i], chunks)

        return Tree(
            chunks,
            tree.chunk_size(),
            tokens,
            tree.token_size(),
            tree.size()
        )


class Tree:
    def __init__(
        self,
        chunks,
        chunk_size,
        tokens,
        token_size,
        size
    ):
        self.chunks = chunks
        self.chunk_size = chunk_size
        self.tokens = tokens
        self.token_size = token_size
        self.size = size

    def __iter__(self):
        return iter(self.chunks)

    def __getitem__(self, key):
        return self.chunks[key]

    @property
    def surface(self):
        return "".join(chunk.surface for chunk in self)

    @property
    def wakati(self):
        return " ".join(chunk.wakati for chunk in self)

    def find(self, function=cabocha.filter._is_function_chunk):
        return cabocha.filter.find(self, function=function)

    def lfind(self, function=cabocha.filter._is_function_chunk):
        return cabocha.filter.lfind(self, function=function)

    def rfind(self, function=cabocha.filter._is_function_chunk):
        return cabocha.filter.rfind(self, function=function)


class Chunk:
    def __init__(
        self,
        chunk_pos,
        additional_info,
        feature_list,
        feature_list_size,
        func_pos,
        head_pos,
        link,
        score,
        token_pos,
        token_size,
        tokens
    ):
        self.id = chunk_pos
        self.additional_info = additional_info
        self.feature_list = feature_list
        self.feature_list_size = feature_list_size
        self.func_pos = func_pos
        self.head_pos = head_pos
        self.link = link
        self.score = score
        self.token_pos = token_pos
        self.token_size = token_size
        self.tokens = tokens

    def __iter__(self):
        return iter(self.tokens)

    def __getitem__(self, key):
        return self.tokens[key]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'Chunk("{self.surface}")'

    @property
    def surface(self):
        return "".join(token.surface for token in self)

    @property
    def wakati(self):
        return " ".join(token.surface for token in self)

    @property
    def next_link(self):
        if self.next_link_id == -1:
            raise EndOfLinkException()
        return self._next_link

    def set_links(self, prev_links, chunks):
        self.next_link_id = self.link
        self.prev_link_ids = prev_links
        self._next_link = chunks[self.next_link_id]
        self.prev_links = [chunks[i] for i in prev_links]

    def has_next_link(self):
        return self.next_link_id >= 0

    def has_prev_links(self):
        return bool(self.prev_links)

    def get_tokens(self, end=None):
        if end >= 0:
            return [token for token in self.tokens if token.id < end]
        else:
            return self.tokens

    def dict(self):
        return {
            "id": self.id,
            "additional_info": self.additional_info,
            "feature_list": self.feature_list,
            "feature_list_size": self.feature_list_size,
            "func_pos": self.func_pos,
            "head_pos": self.head_pos,
            "link": self.link,
            "score": self.score,
            "token_pos": self.token_pos,
            "token_size": self.token_size,
            "tokens": [token.dict() for token in self.tokens],
            "next_link_id": self.next_link_id,
            "prev_link_ids": self.prev_link_ids,
        }

    def find(self, function=cabocha.filter._is_function_token):
        return cabocha.filter.find(self, function=function)

    def lfind(self, function=cabocha.filter._is_function_token):
        return cabocha.filter.lfind(self, function=function)

    def rfind(self, function=cabocha.filter._is_function_token):
        return cabocha.filter.rfind(self, function=function)


class Token:
    def __init__(
        self,
        token_id,
        additional_info,
        feature,
        feature_list,
        feature_list_size,
        ne,
        normalized_surface,
        surface,
    ):
        self.id = token_id
        self.additional_info = additional_info
        self.feature = feature
        self.feature_list = feature_list
        self.feature_list_size = feature_list_size
        self.ne = ne
        self.normalized_surface = normalized_surface
        self.surface = surface

        self.pos = feature_list[0]
        self.pos1 = feature_list[1]
        self.pos2 = feature_list[2]
        self.pos3 = feature_list[3]
        self.ctype = feature_list[4]  # 活用型
        self.cform = feature_list[5]  # 活用形
        self.genkei = feature_list[6]

        # 固有名詞の場合 feature_list に「読み」「発音」は含まれない
        # のでベット処理が必要
        if feature_list_size >= 8:
            self.yomi = feature_list[7]
        else:
            self.yomi = surface

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'Token("{self.surface}")'

    def dict(self):
        return {
            "id": self.id,
            "additional_info": self.additional_info,
            "feature": self.feature,
            "feature_list": self.feature_list,
            "feature_list_size": self.feature_list_size,
            "ne": self.ne,
            "normalized_surface": self.normalized_surface,
            "surface": self.surface,
            "pos": self.pos,
            "pos1": self.pos1,
            "pos2": self.pos2,
            "pos3": self.pos3,
            "ctype": self.ctype,
            "cform": self.cform,
            "genkei": self.genkei,
            "yomi": self.yomi
        }


class EndOfLinkException(Exception):
    """リンク先をもたない Chunk オブジェクトから next_link
    を呼び出した際に発生する例外"""
