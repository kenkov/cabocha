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
        return " ".join(str(token) for token in self)

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

        self.pos = feature_list[0]
        self.pos1 = feature_list[1]
        self.pos2 = feature_list[2]
        self.pos3 = feature_list[3]
        self.genkei = feature_list[6]

    def __str__(self):
        return "{}/{}".format(
            self.surface,
            self.pos
        )


def tokens2str(
    tokens: [Token]
) -> str:
    return " ".join("{}/{}".format(
        token.surface, token.pos
    )for token in tokens)


class CaboChaCaseAnalyzer:
    def __init__(self):
        self.cbc = CaboChaAnalyzer()

    def is_case_chunk(
        self,
        chunk,
    ) -> bool:
        return any(
            token.pos1 in {"格助詞", "係助詞"} for token in chunk
        )

    def is_verb_chunk(
        self,
        chunk
    ) -> bool:
        return (not chunk.has_next_link())

    def ext_verb(
        self,
        chunk
    ) -> [str]:
        """
        [動詞]
        [名詞]+
            動詞-サ変 => [名詞]する
            助動詞 => [名詞]だ

        動詞は次のような例があるので、出現する初めのものをとってくる

            管理/名詞-し/動詞-て/助詞-いる/動詞
        """
        tokens = []
        vflag = False
        for token in chunk:
            pos = token.pos
            if (not vflag) and \
                    (pos in {"動詞", "助動詞", "形容詞", "名詞", "接頭詞"}):
                tokens.append(token)
                vflag = True
            elif vflag and \
                    (pos in {"動詞", "助動詞", "形容詞", "名詞", "接頭詞",
                             "助詞"}):
                if pos == "助動詞" and token.genkei in {"ます", "です", "だ"}:
                    # 例:
                    #   彼は人間である。
                    #   彼は人間です。
                    #   彼は掃除をします。
                    break
                tokens.append(token)
                if pos == "動詞" and token.feature_list[4] == "サ変・スル" and \
                        token.normalized_surface != "さ":
                    # 例:
                    #   彼は運動する
                    # マッチしない例:
                    #   Pythonは開発されている
                    #   Python  名詞,固有名詞,組織,*,*,*,*
                    #   は      助詞,係助詞,*,*,*,*,は,ハ,ワ
                    #   開発    名詞,サ変接続,*,*,*,*,開発,カイハツ,カイハツ
                    #   さ      動詞,自立,*,*,サ変・スル,未然レル接続,する,サ,サ
                    #   れ      動詞,接尾,*,*,一段,連用形,れる,レ,レ
                    #   て      助詞,接続助詞,*,*,*,*,て,テ,テ
                    #   いる    動詞,非自立,*,*,一段,基本形,いる,イル,イル
                    break

                # elif pos == "助詞" and \
                #         token.normalized_surface in {"で"}:
                #     # 例:
                #     #   彼は人間ではない。
                #     #   人間    名詞,一般,*,*,*,*,人間,ニンゲン,ニンゲン
                #     #   で      助詞,格助詞,一般,*,*,*,で,デ,デ
                #     #   は      助詞,係助詞,*,*,*,*,は,ハ,ワ
                #     #   ない    助動詞,*,*,*,特殊・ナイ,基本形,ない,ナイ,ナイ
                #     #   。      記号,句点,*,*,*,*,。,。,。
                #     break
        return tokens

    def ext_case(
        self,
        chunk
    ) -> (Token, [Token]):
        tokens = []
        for token in chunk:
            if token.pos1 in {"格助詞", "係助詞"}:
                #   日本語とは言語である。
                #   日本語は言語である。
                break
            tokens.append(token)

        # 「こと/名詞」に対応
        if tokens and tokens[0].surface == "こと":
            prev_tokens = []
            for prev_chunk in chunk.prev_links:
                prev_tokens = self.ext_case(prev_chunk)[1]
            tokens = prev_tokens + tokens

        return (token, tokens)

    def ext_cases(
        self,
        chunks
    ) -> {str: [Token]}:
        cases = {}
        for chunk in chunks:
            if self.is_case_chunk(chunk):
                kaku, tokens = self.ext_case(chunk)
                kaku_surface = kaku.surface
                if kaku_surface == "って":
                    kaku_surface = "は"
                cases[kaku_surface] = tokens
        return cases

    def verbs2str(
        self,
        tokens
    ) -> str:
        last = []
        if tokens:
            ltoken = tokens[-1]
            sf = ltoken.surface if ltoken.genkei == "*" else ltoken.genkei
            last.append("{}/{}".format(
                sf,
                ltoken.pos
            ))
        return " ".join([str(token) for token in tokens[:-1]] + last)


    def ext_keyword(
        self,
        tokens
    ) -> [str]:
        xs = []
        for token in tokens:
            if token.pos in {"動詞", "形容詞", "名詞"}:
                xs.append("{}/{}".format(token.genkei, token.pos))
        return xs

    def analyze(
        self,
        text
    ) -> dict:
        tree = self.cbc.parse(text)
        dic = {}
        keyword = []
        for chunk in tree:
            if self.is_verb_chunk(chunk):
                verb = self.ext_verb(chunk)
                dic["verb"] = self.verbs2str(verb)
                keyword += self.ext_keyword(verb)
                for case, word in self.ext_cases(chunk.prev_links).items():
                    dic[case] = tokens2str(word)
                    keyword += self.ext_keyword(word)
        dic["keyword"] = keyword
        return dic

    def show_analyze(
        self,
        text
    ):
        dic = self.analyze(text)
        if dic:
            s = "{}".format(dic["verb"])
            for case, word in dic["cases"].items():
                s += "\n    {}: {}".format(case, word)
        else:
            s = ""
        return s


if __name__ == '__main__':
    import sys

    analyzer = CaboChaAnalyzer()

    fd = open(sys.argv[1]) if len(sys.argv) >= 2 else sys.stdin

    for text in (_.strip() for _ in fd):
        tree = analyzer.parse(text)
        for chunk in tree:
            if chunk.has_next_link():
                print("{} => {} => {}".format(
                    [str(c) for c in chunk.prev_links],
                    str(chunk),
                    str(chunk.next_link)
                ))
