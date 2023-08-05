Solarized Sphinx Theme
==============================================================================

.. sidebar:: Solarizedとは

    Solarized <http://ethanschoonover.com/solarized> とはCIELAB色空間という
    ものに準じて、Ethan Schoonoverという方が作成されたColorschemeです。
    dark背景とlight背景の2パターンがありますが、このテーマではlightテーマ
    を使用させて頂いております。

    ちなみに上記サイトではVimやEmacs、iTerm2等様々なSolarizedが
    公開されています。

Colorschemeの `Solarized <http://ethanschoonover.com/solarized>`_ で
作成したテーマです。

Vimの配色をSolarizedにしたところ、非常に見易く、目も疲れにくくなった気がして
大変気に入ったので、コーディングと同じように長時間画面と睨めっこする事が多い
ドキュメントでも有効なのではないかという想いから作成しました。

インストール
------------------------------------------------------------------------------

.. code-block:: bash

   pip install sphinxjp.themes.solarized 

conf.pyの設定
------------------------------------------------------------------------------

.. code-block:: python
    
    extensions = ['sphinxjp.themecore', 'sphinxjp.themes.solarized']
    pygments_style = 'solarized'
    html_theme = 'solarized'



**このテーマに加えて以下も同時に設定するとより効果的です。**

フォントのインストール
------------------------------------------------------------------------------

* `Migu 1VS <http://mix-mplus-ipa.sourceforge.jp/>`_ フォント
* `Ricty <http://save.sys.t.u-tokyo.ac.jp/~yusa/fonts/ricty.html>`_ フォント
  または `Migu 1M <http://mix-mplus-ipa.sourceforge.jp/>`_ フォント

.. note::

    Windowsの場合は gdipp <http://code.google.com/p/gdipp/> や
    ezgdi <http://code.google.com/p/ezgdi/> 等で表示を調整してください。

Pygments Styleの追加
------------------------------------------------------------------------------

SphinxではSyntax HighlightにPygmentsを使用しています。
PygmentsもSolarizedにすることでスタイルに統一感をもたせます。
ここでは `solarized-pygment <https://bitbucket.org/john2x/solarized-pygment>`_
を使用させて頂いております。

.. code-block:: bash

    cp -a solarized.py /path/to/site-packages/pygments/styles/ 

コンテンツ:

.. toctree::
   :maxdepth: 2

   sample

Indices and tables
==============================================================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

