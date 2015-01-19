#! /usr/bin/env python
# coding:utf-8

import CaboCha
from collections import defaultdict


class CaboChaAnalyzer:
    def __init__(self):
        self.parser = CaboCha.Parser()

    def parse(self, text):
        tree = self.parser.parse(text)

        chunks = []
        tokens = []
        prev_links_dic = defaultdict(list)
        for chunk_pos in range(tree.chunk_size()):
            chunk_tokens = []
            chunk = tree.chunk(chunk_pos)
            for j in range(chunk.token_size):
                token = tree.token(chunk.token_pos + j)
                mytoken = Token(
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


class Chunk:
    def __init__(
        self,
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

    def __str__(self):
        return "-".join(token.normalized_surface for token in self)

    def set_links(self, prev_links, chunks):
        self.next_link_id = self.link
        self.prev_link_ids = prev_links
        self.next_link = chunks[self.next_link_id]
        self.prev_links = [chunks[i] for i in prev_links]

    def has_next_link(self):
        return self.next_link_id >= 0

    def has_prev_links(self):
        return bool(self.prev_links)


class Token:
    def __init__(
        self,
        additional_info,
        feature,
        feature_list,
        feature_list_size,
        ne,
        normalized_surface,
        surface,
    ):
        self.additional_info = additional_info
        self.feature = feature
        self.feature_list = feature_list
        self.feature_list_size = feature_list_size
        self.ne = ne
        self.normalized_surface = normalized_surface
        self.surface = surface


if __name__ == '__main__':

    text = "今日は伝説のステーキを食べに行きますっ。"
    tree = CaboChaAnalyzer().parse(text)

    for chunk in tree:
        if chunk.has_next_link():
            print("{} => {} => {}".format(
                [str(c) for c in chunk.prev_links],
                str(chunk),
                str(chunk.next_link)
            ))
