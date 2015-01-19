==============================
CaboCha wrapper
==============================

日本語係り受け解析器 `CaboCha <https://code.google.com/p/cabocha/>`_
をｂｅｎｒｉに使うためのラッパモジュールです。


例
===

.. code-block:: python

    >>> from cabocha import CaboChaAnalyzer
    >>>
    >>> text = "今日は伝説のステーキを食べに行きます。"
    >>> tree = CaboChaAnalyzer().parse(text)
    >>>
    >>> for chunk in tree:
    ...     if chunk.has_next_link():
    ...         print("{} => {} => {}".format(
    ...             [str(c) for c in chunk.prev_links],
    ...             str(chunk),
    ...             str(chunk.next_link)
    ...         ))
    ...
    [] => 今日-は => 行き-ます-っ-。
    [] => 伝説-の => ステーキ-を
    ['伝説-の'] => ステーキ-を => 食べ-に
    ['ステーキ-を'] => 食べ-に => 行き-ます-。
