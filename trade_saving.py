from bitmex_simple_websocket import BitMEXWebSocket 
import json 


import datetime
import sqlite3


# API = 'ZHVnSMpBwfQuXffB9HwcV7PO'
# SECRET = 'Tpl9yMM_27sXONxdiblrfploRWFaziEvadSwq82fyk32Zu12'


class MyBitMEXWebsocket(BitMEXWebSocket):  #BitMEXWebSocketをオーバーライド
    def on_message(self, ws, message):  #データ(message)を受信したときに呼ばれる関数
        data = json.loads(message)  #受信したデータをPythonの変数に変換

        if'table' in data and data["table"] == "trade":#tradeピン
            print("trade"+str(data['data'][0]))

    
            d_today = datetime.date.today()
            conn = sqlite3.connect("trade_{}.db".format(d_today))
            
            c = conn.cursor()
            
            
            #テーブルの存在確認
            cur = c.execute("SELECT * FROM sqlite_master WHERE type='table' and name='%s'" % "trade")
            if cur.fetchone() == None: #存在してないので作る
               
                c.execute('create table trade (timestamp, symbol, side, size, price, tickDirection, trdMatchID, grossValue, homeNotional, foreignNotional)')
            
           
            current_data = data['data'][0]

            
            sql = 'insert into trade (timestamp, symbol, side, size, price, tickDirection, trdMatchID, grossValue, homeNotional, foreignNotional) values (?,?,?,?,?,?,?,?,?,?)'
            finaldata = (current_data['timestamp'],current_data['symbol'],current_data['side'],current_data['size'],current_data['price'],current_data['tickDirection'],current_data['trdMatchID'],current_data['grossValue'],current_data['homeNotional'],current_data['foreignNotional'])
            
            c.execute(sql, finaldata)

            conn.commit()
            del current_data
            del sql
            del finaldata

                
bitmex = MyBitMEXWebsocket(endpoint='wss://www.bitmex.com/realtime?subscribe=trade:XBTUSD') 
