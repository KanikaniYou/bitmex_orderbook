# BitmexのOrderBookをWebSocketで受信しSQLiteに保存

## 概要
Bitmexの板情報(order book他)はその多くがWebSocketで受信可能です。
Pythonのモジュールも公開されており、それを利用してSQLiteで5秒足OHLCを作成、保存するスクリプトを作成しました。スキャルピングのボットに使えそうですね。
また、直近360本をCSVで保存するスクリプトを用意しました。そしてそのCSVの使用例としてシステムトレードボットの例も書きましたが、こちらのロジックはスキャルピングの注文の例であり、実際の運用では100%損失を出します。


## 環境
Cloud9 Python3.6.5

## 使い方

```pip install -r requirements.txt```

でセットアップできます。

```trade_saving.py```

でSQLiteファイルの作成ができます。上のpythonファイルの設定によって任意の間隔で価格情報を保存できます。

```data_to_short_csv.py```

で直近360本のOHLCをCSVにしたものが常時更新されます。

scal_test.pyはAPIKeyを入力することで実際に注文まで行えます。仮

## 注意
繰り返しになりますが、ボットは利益を出すロジックになっていません。
