# coding: UTF-8
import time
import requests
import ccxt
from datetime import datetime
import calendar
import pandas as pd
import bitmex
from retrying import retry, RetryError

bitmex_ccxt = ccxt.bitmex({
    'apiKey': '',
    'secret': '',
})
# bitmex_ccxt.urls['api'] = bitmex_ccxt.urls['test']

summary = bitmex_ccxt.privateGetUserWalletSummary()

client = bitmex.bitmex(test=False, api_key="", api_secret="")

open_size = 0

LEVERAGE = 25.0

SHOKO_RITSU = 0.01

error_count = 0

error_past = 0

error_second = 0

posnotify_flag = False

posnotify_flag_2 = False


@retry(stop_max_attempt_number=10,wait_fixed=3000)
# def order_limit(size, price):
#     order = bitmex_ccxt.privatePostOrder(dict({ 'symbol': 'XBTUSD', 'orderQty': size, 'price': price }))
#     return order
def order_limit(size, price):
	order = client.Order.Order_new(symbol='XBTUSD', orderQty=size, price=price).result()



SAR_Step = 0.01
SAR_Maximum = 0.1
SAR_EP_Offset = 3


SAR_Side = True

LastTrendFrag = False


bitmex_ccxt.private_post_position_leverage({"symbol":"XBTUSD", "leverage": str(LEVERAGE)})
#レバレッジ変更



while True:
    try:
	
        df = pd.read_csv('realtime_ohlc_5sec_360.csv')
        availableMargin = bitmex_ccxt.fetch_balance()['info'][0]['availableMargin']
        # summary = bitmex_ccxt.privateGetUserWalletSummary()

        print('##########################')
        print(str(datetime.fromtimestamp(round(time.time()+ 60 * 60 * 9)))) 
        pos = bitmex_ccxt.private_get_position()[0]['currentQty']   #########################怪しい
        print("現在のポジションは"+str(pos))
        print("証拠金残高は"+ str((summary[2]['marginBalance']) * 0.00000001)+"XBT")  #########################怪しい
        # fetchOpenOrders = bitmex_ccxt.fetchOpenOrders('BTC/USD')
        open_size = int((availableMargin) * LEVERAGE * SHOKO_RITSU * 0.00000001 * df['Close'][359]) 
        # iSAR(df,SAR_Step,SAR_Maximum,SAR_EP_Offset)
        # def iSAR(dfSAR, step, maximum, offset):
        last_period = 0
        dir_long = True
        ACC = SAR_Step
        SAR = df['Close'].astype(float).copy()
        offset = SAR_EP_Offset
        step = SAR_Step
        maximum = SAR_Maximum
    	
    	
        for i in range(1,len(df)):
            last_period += 1    
            
            if dir_long == True:
            
                listData = []
                Ep1 = df['Close'][i-last_period:i].astype(float).max()
                SAR[i] = SAR[i-1]+ACC*(Ep1-SAR[i-1])
                Ep0 = max([Ep1, df['Close'][i].astype(float)])
                if Ep0 > Ep1 and ACC+step <= maximum: 
                    ACC+=step
                    #print("fromSAR:"+str(TrendHeadFrag))
                if SAR[i] > df['Close'][i].astype(float):
                    dir_long = False
                    SAR[i] = Ep0+offset
                    last_period = 0
                    ACC = step
                    
                    #print("fromSAR:"+str(TrendHeadFrag))
                if dir_long == True:
                    SAR_Side = True
                    #print("fromSAR,SAR_Side:"+str(SAR_Side))
                else:
                    SAR_Side = False
                    #print("fromSAR,SAR_Side:"+str(SAR_Side))
                
            else:
            
                listData = []
                Ep1 = df['Close'][i-last_period:i].astype(float).min()
                SAR[i] = SAR[i-1]+ACC*(Ep1-SAR[i-1])
                Ep0 = min([Ep1, df['Close'][i].astype(float)])
                if Ep0 < Ep1 and ACC+step <= maximum: 
                    ACC+=step
                    #print("fromSAR:"+str(TrendHeadFrag))

                if SAR[i] < df['Close'][i].astype(float):
                    dir_long = True
                    SAR[i] = Ep0-offset
                    last_period = 0
                    ACC = step
                    
                    #print("fromSAR:"+str(TrendHeadFrag))
                if dir_long == True:
                    SAR_Side = True
                    #print("fromSAR,SAR_Side:"+str(SAR_Side))
                else:
                    SAR_Side = False
                    #print("fromSAR,SAR_Side:"+str(SAR_Side))


        if LastTrendFrag != SAR_Side:
        	

            orders = bitmex_ccxt.fetch_open_orders("BTC/USD")
            for order in orders:
                bitmex_ccxt.cancel_order(order["id"], order["symbol"])

            if pos > 0 and SAR_Side == False:
                order_limit(int(-pos*1.0),df['Close'][359]+0.5)
            elif pos < 0 and SAR_Side == True:
                order_limit(int(-pos*1.0),df['Close'][359]-0.5)
            else:
                pass

        if SAR_Side == True:
            if open_size > 20:
                order_limit(open_size,df['Close'][359]-0.5)
                print("LongOrder,size:"+str(open_size)+"LimitPrice:"+str(df['Close'][359]-0.5))
        else:
            if open_size > 20:
                order_limit(-open_size,df['Close'][359]+0.5)
                print("ShortOrder,size:"+str(open_size)+"LimitPrice:"+str(df['Close'][359]+0.5))
        print("SAR_Side:"+str(SAR_Side))
        LastTrendFrag = SAR_Side
        time.sleep(6)

    except Exception as e:
        print('%r' % e)
        time.sleep(10)
        error= '%r' % e
        log_string = "\n"+str(datetime.now())+str(error)
        with open("log_scal_test_error.txt", "a", encoding="utf-8") as f:
            f.write(log_string)

        