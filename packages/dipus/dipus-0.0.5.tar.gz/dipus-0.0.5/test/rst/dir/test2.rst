テンプレートを作成する
===========================
出力されるドキュメントのひな型としてHTMLのテンプレートを作成します。
Sphinxでは、デフォルトのHTMLテンプレートとして\ `Jinja
<http://jinja.pocoo.org/>`_\ が使用されます。

必要となるテンプレート
-------------------------
オリジナルのテーマを作成する際に、最低限必要なテンプレートは次のテンプ
レートです。

* ドキュメント全体の基礎となるテンプレート
* 基礎となるテンプレートを基にドキュメントを表示するテンプレート

以降の例では、前者のテンプレートを\ ``layout.html``\ 、後者のテンプレー
トを\ ``page.html``\ とします。

Sphinxでは、作成したドキュメント(.rstのファイル)の他に、検索ページ
(search.html)や、索引ページ(genindex.html)も生成されます。次の様に\
``theme.conf``\ で継承元を指定しない場合には、生成される全てのページに
対してのテンプレートが必要になります。

\ ``theme.conf``\ で、以下の様に継承元のテーマを指定すれば、実際に全て
のドキュメントに対してテンプレートを作成する必要はありません。オリジナ
ルテーマで用意していないテンプレートの代わりに継承元の\ ``basic``\ テー
マで用意されているテンプレートが適用されます。 ::

    inherit = basic

ドキュメントの枠組みを作成する
-------------------------------
テーマディレクトリ内に\ ``layout.html``\ を作成し、基本となる枠組みを
作成します。Jinjaの記法については、\  `公式のドキュメント
<http://jinja.pocoo.org/2/documentation/>`_\ を参照してください。

\ ``layout.html``\ には、全ページ共通のヘッダー、サイドバー、ドキュメ
ント部、フッターを記述します。

.. code-block:: jinja

  {%- block doctype %}
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  {%- endblock doctype %}
  <html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html;
    charset=UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ pathto('_static/' + style, 1) }}"
    type="text/css" />
  </head>
  <body>
  <div id="wrapper">
  {%- block header %}
    <div id="header">
      <h1>header</h1>
    </div>
  {%- endblock header %}
  {%- block sidebar %}
    <div id="sidebar">
      <h2>sidebar</h2>
    </div>
  {%- endblock sidebar %}
  {%- block document %}
    <div id="document">
      <h2>document</h2>
      {%- block body %}{%- endblock body %}
    </div>
  {%- endblock document %}
  </div>
  {%- block footer %}
  <div id="footer">
    <h1>footer</h1>
  </div>
  {%- endblock footer %}
  </body>
  </html>

次に、各ページのドキュメント内容を読み込む\ ``page.html``\ を作成し、
各ドキュメントの内容を読み込みます。

.. code-block:: jinja

   {% extends "!layout.html" %}
   {% block body %}
   {{ body }}
   {% endblock body %}

\ ``page.html``\ では、\ ``{% extends "!layout.html" %}``\ の様に\
``layout.html``\ を継承します。テンプレートの継承については
:ref:`extends` を参照して下さい。

一旦、ドキュメントの出力内容を確認するために、以下のスタイルシートを適
用しました。

main.css

.. code-block:: css

  #header {
    background-color: #a2e8fe;
  }

  #sidebar {
    background-color: #4b7afd;
    float: left;
    width: 20%;
  }

  #document {
    background-color: #f7fed3;
    float:left;
    width: 80%;
  }

  #footer {
    background-color: #fcc1c1;
    clear: both;
  }

  h1 {
    margin: 0;
  }


この\ ``main.css``\ は、テーマディレクトリ内の\ ``staticディレクトリ
``\ 内に配置します。

ここで、\ ``make html``\ コマンドでドキュメントを生成すれば、オリジナ
ルのテーマを適用したドキュメントは以下の様になります。

.. _extends:

テンプレートを継承する
--------------------------
現在のところ、以下のパーツから成るドキュメントのテンプレートを作成して
います。

* header
* sidebar
* document
* footer

このドキュメントに足りていないサイドバー内のパーツ、リレーションバーを
作成します。
以下のスクリーンショットは"basic"テーマを適用した際の各バーツです。

実際のところ、上記のパーツを1から作る必要はありません。ここでは、
"basic"テーマの\ ``layout.html``\ を継承して、各パーツをオリジナルのテー
マに組込みます。

"basic"テーマのテンプレートを継承する場合は、テンプレートの先頭に以下
の1行を記述します。

.. code-block:: jinja

   {% extends "継承元のテーマ名/継承するテンプレート" %}

継承元のテーマ名を省略した場合は、同テーマ内のテンプレートを継承します。

他のテンプレートを継承した場合、オリジナルテーマの\ ``layout.html``\
に記述するべきパーツは、継承元のテンプレートとの差異になる部分だけです。
以下の\ ``layout.html``\ では、"basic"テーマの\ ``layout.html``\ を継
承して、新たにオリジナルのヘッダを追加しています。

**layout.html**

.. code-block:: jinja

   {% extends "basic/layout.html" %}
   {%- block header %}
   <div id="header">
       <p>オリジナルヘッダ</p>
   </div>
   {%- endblock header %}

追加したヘッダ以外は、"basic"テーマのテンプレートが適用されるため、サ
イドバー内の目次や検索ボックス、リレーションバーが生成されています。

また、継承元のテンプレートで用意されているバーツに、さらにオリジナルテー
マのパーツを加えたい場合があります。

以下の例では、"basic"テーマのリレーションバーに、外部サイトへのリンク
を追加します。

.. code-block:: jinja

    {% extends "basic/layout.html" %}
    {% block header %}
    <div id="header">
        <p>オリジナルのヘッダ</p>
    </div>
    {% endblock header %}
    {% block relbar1 %}
    <a href="http://projecthome.com/">Project Homepage</a>
    {{ super() }}
    {% endblock relbar1 %}

\ ``relbar1``\ ブロックを定義する際に、\ ``{{ super() }}``\ と記述して
いる事に注意してください。

\ ``{{ super() }}``\ は、継承元のテンプレートで定義されている内容を維
持したい場合に記述します。記述しない場合には、継承元のブロックを上書き
するため、継承元の内容は表示されません。

テンプレートを継承する方法として、以下のように"!"を記述する方法もあり
ます。

.. code-block:: jinja

   {% extends "!layout.html" %}

"!"を継承するテンプレート名につける事で、ユーザが用意したテンプレート
を継承元として参照する事になります。


ユーザが用意したテンプレートとは、"conf.py"の ``templates_path`` で設
定されているパスに配置されているものです。ドキュメントに使用されるテン
プレートは以下の順番で探索されます。

* ``template_path``\ で指定されたディレクトリ内のテンプレート
* 選択されたテーマ内のテンプレート
* テーマが継承しているテンプレート

"basic"テーマでは、Sphinxで作成されたドキュメントの基本になるテンプレー
トが提供されています。"basic"テーマに組み込まれているパーツ(ブロック)
や組込の関数、変数を利用する事で、さらに細かいオリジナルテーマを作成す
る事ができます。

"basic"テーマに組み込まれているパーツ(ブロック)や関数については、
Sphinxドキュメントの\ `組み込みテンプレートの働き
<http://sphinx.shibu.jp/templating.html#id2>`_\ を参照してください。
