#! /usr/bin/env python
# coding:utf-8

from pred import Pred


class PredNotFoundException(Exception):
    """述語が見つからない時に発生する例外"""


def _is_pred_token(token):
    return token.pos in {"動詞", "形容詞"} or token.genkei in {"です"}


def find_preds(tree, is_pred_token):
    ids = []
    for chunk in tree.chunks:
        for token in chunk:
            if is_pred_token(token):
                ids.append((chunk.id, token.id))
    return [
        Pred(tree, chunk_id, token_id)
        for chunk_id, token_id in ids
    ]


def rfind_pred(tree, is_pred_token):
    for chunk in reversed(tree.chunks):
        for token in reversed(chunk.tokens):
            if is_pred_token(token):
                return Pred(tree, chunk.id, token.id)
    raise PredNotFoundException()


def find_pred(tree, is_pred_token):
    for chunk in tree.chunks:
        for token in chunk:
            if is_pred_token(token):
                return Pred(tree, chunk.id, token.id)
    raise PredNotFoundException()
