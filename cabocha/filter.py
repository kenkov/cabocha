#! /usr/bin/env python
# coding:utf-8


class NotFoundException(Exception):
    """述語が見つからない時に発生する例外"""


def _is_function_token(token):
    return token.pos in {"動詞", "形容詞", "名詞"}


def _is_function_chunk(chunk):
    for token in chunk:
        if _is_function_token(token):
            return True
    return False


def find(iters, function):
    res = []
    for item in iters:
        if function(item):
            res.append(item)
    return res


def rfind(iters, function):
    for item in reversed(iters):
        if function(item):
            return item
    raise NotFoundException()


def lfind(iters, function):
    for item in iters:
        if function(item):
            return item
    raise NotFoundException()
