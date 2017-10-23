===================================
CaboCha wrapper package for Python
===================================

日本語係り受け解析器 `CaboCha <http://taku910.github.io/cabocha/>`_
を Python から便利に使うためのラッパーパッケージです。


インストール
==============

はじめに、 `CaboCha 公式ページ <http://taku910.github.io/cabocha/>`_
にしたがって CaboCha をインストールしてください。
MacOS で Homebrew を使用している場合は、cabocha および mecab-ipadic パッケージを
インストールできます。

次に CaboCha の Python バインディングをインストールします。

::

    git clone https://github.com/taku910/cabocha
    cd cabocha
    pip install python/

最後にこのリポジトリを clone し、pip にてインストールしてください。

::

    git clone https://github.com/kenkov/cabocha
    pip install cabocha/


使い方
======

係り受け解析をする

::

    >>> from cabocha.analyzer import CaboChaAnalyzer
    ... analyzer = CaboChaAnalyzer()
    ... tree = analyzer.parse("日本語の形態素解析はすごい")
    ... for chunk in tree:
    ...     for token in chunk:
    ...         print(token)
    ...
    Token("日本語")
    Token("の")
    Token("形態素")
    Token("解析")
    Token("は")
    Token("すごい")

チャンクの係り先をたどる

::

    >>> chunks = tree.chunks
    >>> start_chunk = chunks[0]
    >>> start_chunk.next_link
    Chunk("形態素解析は")
    >>> start_chunk.next_link.next_link
    Chunk("すごい")
    >>> # 次の呼び出しは EndOfLinkException 例外が発生する
    >>> # start_chunk.next_link.next_link.next_link


チャンクの係り元を辿る

::

    >>> end_chunk = chunks[-1]
    >>> end_chunk.prev_links
    [Chunk("形態素解析は")]
    >>> end_chunk.prev_links[0].prev_links
    [Chunk("日本語の")]
    >>> end_chunk.prev_links[0].prev_links[0].prev_links
    []

特定の条件に当てはまるチャンクやトークンを取り出す

::

    >>> tree.find(function=lambda chunk: any(token.pos == "名詞" for token in chunk))
    [Chunk("日本語の"), Chunk("形態素解析は")]
    >>> tree.find(function=lambda chunk: any(token.pos == "形容詞" for token in chunk))
    [Chunk("すごい")]
