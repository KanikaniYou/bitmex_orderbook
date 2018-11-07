import pandas as pd
import sqlite3
import datetime
import time

interval = 5
#欲しい足の秒数。5秒足なら5

time_interval = 2
#更新したい時間間隔　5秒ごとに更新したいのであれば5 interval に従うのであればその式

each_data_time_interval = 4
#一度にdbから取得する時間。4秒分なら4

OutputCSV_name = 'realtime_ohlc_360bars.csv'

while True:
    try:
        d_today = datetime.date.today()

        dbpath = 'trade_{}.db'.format(d_today)
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        
        TimeNow = datetime.datetime.now()
        startTime = TimeNow - datetime.timedelta(seconds=each_data_time_interval)

        startYear = startTime.strftime('%Y')
        startMonth = startTime.strftime('%m')
        startDay = startTime.strftime('%d')
        startHour = startTime.strftime('%H')
        startMinute = startTime.strftime('%M')
        startSec = startTime.strftime('%S')
        startMiliSec = startTime.strftime('%f')[0:3]
        
        endYear = TimeNow.strftime('%Y')
        endMonth = TimeNow.strftime('%m')
        endDay = TimeNow.strftime('%d')
        endHour = TimeNow.strftime('%H')
        endMinute = TimeNow.strftime('%M')
        endSec = TimeNow.strftime('%S')
        endMiliSec = TimeNow.strftime('%f')[0:3]

        if int(startSec)//interval == int(endSec)//interval: #each_data_time_intervalが足の中にあればただ最新の行を更新する
            cursor.execute("SELECT * FROM trade WHERE timestamp BETWEEN '{0}-{1}-{2}T{3}:{4}:{5}.{6}Z' AND '{7}-{8}-{9}T{10}:{11}:{12}.{13}Z'".format(startYear,startMonth,startDay,startHour,startMinute,startSec,startMiliSec,endYear,endMonth,endDay,endHour,endMinute,endSec,endMiliSec))
            res = cursor.fetchall()
            ohlcv_list =[]
            for x in res:
                ohlcv_list.append(res[len(res)-1][4]) #直近で入力するohlcvのリストに対象データのpriceを格納
            print(ohlcv_list)
            
            if len(ohlcv_list) == 0:
                print("データ更新なし")
            else:
                df = pd.read_csv(OutputCSV_name)
                if int(df.at[359,'High']) < max(ohlcv_list):
                    df.at[359,'High'] = max(ohlcv_list)
                if int(df.at[359,'Low']) > min(ohlcv_list):
                    df.at[359,'Low'] = min(ohlcv_list)
                df.at[359,'Close'] = ohlcv_list[-1]
                df.to_csv(OutputCSV_name ,mode='w',index=False)
                print("最新のみ足を更新")
                print("##############")
        
        else:#each_data_time_intervalが足をまたいでいるので、足までとその後で切り、足までは更新、その後はもし作成されていなければ作成し、作成されていれば更新
            df = pd.read_csv(OutputCSV_name)
            tdatetime = datetime.datetime.strptime(df.at[359,'time'], '%Y.%m.%d %H-%M-%S')
            tdate = datetime.datetime(tdatetime.year, tdatetime.month, tdatetime.day,tdatetime.hour, tdatetime.minute,tdatetime.second)
            before = TimeNow
            after = before.strftime('%Y.%m.%d %H-%M-%S')
            str_list = list(after)
            str_list[17:19] = str((int(endSec)//interval)*interval)
            str_changed = "".join(str_list)
            separate_time = datetime.datetime.strptime(str_changed, '%Y.%m.%d %H-%M-%S')
            sepaYear = separate_time.strftime('%Y')
            sepaMonth = separate_time.strftime('%m')
            sepaDay = separate_time.strftime('%d')
            sepaHour = separate_time.strftime('%H')
            sepaMinute = separate_time.strftime('%M')
            sepaSec = separate_time.strftime('%S')
            sepaMiliSec = separate_time.strftime('%f')[0:3]
            
            if tdate + datetime.timedelta(seconds=interval) < datetime.datetime.now(): #最新足は作成されていない
                '''
                後半のデータで最新足を作成
                '''
                data_startSec = '%02d' % ((int(startSec)//(interval))*interval) #intervalごとで正規化
                dataTimeSec =  '%02d' % ((int(endSec)//(interval))*interval)
                dataTime = "{0}.{1}.{2} {3}-{4}-{5}".format(endYear,endMonth,endDay,endHour,endMinute,dataTimeSec)
 
                #後半のデータはseparate_timeからTimeNowまで

                cursor.execute("SELECT * FROM trade WHERE timestamp BETWEEN '{0}-{1}-{2}T{3}:{4}:{5}.{6}Z' AND '{7}-{8}-{9}T{10}:{11}:{12}.{13}Z'".format(startYear,startMonth,startDay,startHour,startMinute,startSec,startMiliSec,endYear,endMonth,endDay,endHour,endMinute,endSec,endMiliSec))
                res = cursor.fetchall()
                ohlcv_list =[]
                for x in res:
                    ohlcv_list.append(res[len(res)-1][4]) #直近で入力するohlcvのリストに対象データのpriceを格納
                print(ohlcv_list)
                
                if len(ohlcv_list) == 0: #もし後半に更新するデータがなければ
                    Open = df.at[359,'Close']
                    High = df.at[359,'Close']
                    Low = df.at[359,'Close']
                    Close = df.at[359,'Close']
                    df2 = pd.DataFrame({'time':[dataTime],'Open':[Open], 'High':[High], 'Low':[Low], 'Close': [Close]},index=[360])
                    df_append = df.append(df2,sort=False)
                    df_append_deleted = df_append.drop(0,axis=0)
                    df_append_deleted.to_csv(OutputCSV_name,mode='w',index=False)
                    print("前回足の終値で最新足を作成")

                else:
                    Open = df.at[359,'Close']
                    High = max(ohlcv_list)
                    Low = min(ohlcv_list)
                    Close = ohlcv_list[-1]
                    df2 = pd.DataFrame({'time':[dataTime],'Open':[Open], 'High':[High], 'Low':[Low], 'Close': [Close]},index=[360])
                    df_append = df.append(df2,sort=False)
                    df_append_deleted = df_append.drop(0,axis=0) #1行目を削除
                    df_append_deleted.to_csv(OutputCSV_name,mode='w',index=False)
                    print("最新足作成")

                '''
                前半のデータ挿入
                '''
                df = pd.read_csv(OutputCSV_name)
                data_endSec = '%02d' % ((int(endSec)//(interval))*interval) #intervalごとで正規化
                cursor.execute("SELECT * FROM trade WHERE timestamp BETWEEN '{0}-{1}-{2}T{3}:{4}:{5}.{6}Z' AND '{7}-{8}-{9}T{10}:{11}:{12}.{13}Z'".format(startYear,startMonth,startDay,startHour,startMinute,startSec,startMiliSec,sepaYear,sepaMonth,sepaDay,sepaHour,sepaMinute,sepaSec,sepaMiliSec))
                res = cursor.fetchall()
                last_ohlcv_list =[]
                for x in res:
                    last_ohlcv_list.append(res[len(res)-1][4]) #直近で入力するohlcvのリストに対象データのpriceを格納
                print(last_ohlcv_list)
                if len(last_ohlcv_list) == 0:
                    print("前回足での新たな更新分はなし")
                    print("##############")
                else:
                    if max(last_ohlcv_list) > int(df.at[358,'High']) :
                        df.at[358,'High'] = max(last_ohlcv_list)
                    else:
                        pass
                    if min(last_ohlcv_list) < int(df.at[358,'Low']):
                        df.at[358,'Low'] = min(last_ohlcv_list)
                    else:
                        pass
                    df.at[358,'Close'] = last_ohlcv_list[-1]
                    df.at[359,'Open'] = last_ohlcv_list[-1]
                    df.to_csv(OutputCSV_name,mode='w',index=False)
                    print("最新足のOpenも更新")
                    print("##############")

            else: #データがすでに作成されている
                '''
                後半のデータ挿入
                '''
                data_startSec = '%02d' % ((int(startSec)//(interval))*interval) #intervalごとで正規化
                dataTime = "{0}.{1}.{2} {3}-{4}-{5}".format(startYear,startMonth,startDay,startHour,startMinute,data_startSec)
                cursor.execute("SELECT * FROM trade WHERE timestamp BETWEEN '{0}-{1}-{2}T{3}:{4}:{5}.{6}Z' AND '{7}-{8}-{9}T{10}:{11}:{12}.{13}Z'".format(sepaYear,sepaMonth,sepaDay,sepaHour,sepaMinute,sepaSec,sepaMiliSec,endYear,endMonth,endDay,endHour,endMinute,endSec,endMiliSec))
                res = cursor.fetchall()
                ohlcv_list =[]
                for x in res:
                    ohlcv_list.append(res[len(res)-1][4]) #直近で入力するohlcvのリストに対象データのpriceを格納
                print(ohlcv_list)
                if len(ohlcv_list) == 0:
                    print("最新足更新データなし")
                    print("##############")
                else:
                    df = pd.read_csv(OutputCSV_name)
                    if max(ohlcv_list) > int(df.at[359,'High']):
                        df.at[359,'High'] = max(ohlcv_list)
                    else:
                        pass
                    if min(ohlcv_list) < int(df.at[359,'Low']):
                        df.at[359,'Low'] = min(ohlcv_list)
                    else:
                        pass
                    df.at[359,'Close'] = ohlcv_list[-1]
                    df.to_csv(OutputCSV_name,mode='w',index=False)
                    print("最新足を更新")
                    print("##############")
        time.sleep(time_interval)

    except Exception as e:
        print('%r' % e)
        error= '%r' % e
        log_string = "\n"+str(datetime.datetime.now())+str(error)
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(log_string)

        error= '%r' % e
        

        time.sleep(time_interval)