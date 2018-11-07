# BitmexのOrderBookをWebSocketで受診しSQLiteに保存

## 概要
Bitmexの板情報(order book)は多くがWebSocketで受信可能です。
Pythonのモジュールも公開されており、それを利用してSQLiteで保存するスクリプトを作成しました。
また、使用例としてシステムトレードの例も書きましたが、こちらのロジックはスキャルピングの注文のやり方の例であり、実際の運用では100%損失を出します。
***DEMO:***
![result](https://github.com/KanikaniYou/bitmex_orderbook/trade_save3.gif)

##環境
Cloud9 Python3.6.5

## 使い方

```pip install -r requirements.txt```
