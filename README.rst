==============================
CaboCha wrapper
==============================

日本語係り受け解析器 `CaboCha <https://code.google.com/p/cabocha/>`_
を便利に使うためのラッパーパッケージです。


インストール
==============

はじめに、CaboCha の Python バインディングをインストールします。

次にこのリポジトリを clone し、pip にてインストールしてください。

::

    git clone https://github.com/kenkov/cabocha
    pip install cabocha/


使い方
======

係り受け解析をする

::

    >>> from cabocha.analyzer import CaboChaAnalyzer
    >>> analyzer = CaboChaAnalyzer()
    >>> tree = analyzer.parse("日本語の形態素解析はすごい")
    >>> for chunk in tree:
    ...     for token in chunk:
    ...         print(token.pos, token.pos1, token.surface)
    ...
    名詞 一般 日本語
    助詞 連体化 の
    名詞 一般 形態素
    名詞 サ変接続 解析
    助詞 係助詞 は
    形容詞 自立 すごい

チャンクの係り先をたどる

::

    >>> chunks = tree.chunks
    >>> chunks[0].surface
    '日本語の'
    >>> chunks[0].next_link.surface
    '形態素解析は'
    >>> chunks[0].next_link.next_link.surface
    'すごい'
    >>> chunks[0].next_link.next_link.next_link.surface
    'すごい'

# チャンクの係り元を辿る

::

    >>> chunks[-1].prev_links[0].surface
    '形態素解析は'
    >>> chunks[-1].prev_links[0].prev_links[0].surface
    '日本語の'
    >>> chunks[-1].prev_links[0].prev_links[0].prev_links
    []

特定の条件に当てはまるチャンクやトークンを取り出す

::

    >>> res = tree.find(function=lambda chunk: any(token.pos == "名詞" for token in chunk))
    >>> len(res)
    2
    >>> [item.surface for item in res]
    ['日本語の', '形態素解析は']
