from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from datetime import datetime,timezone,timedelta
import random
# from datetime import datetime
import sys
import os

app = Flask(__name__)

# Channel Access Token
line_bot_api  = LineBotApi('abGHwk0OES+qGhHVtwVT4qUIALZuJNCwkhOU99Y1HEoSnBfMah8q+e/c+sUbsxJxkhsJW8A5Mm91Y7NL3GWPETTmzB/jdiRPgxWa82KYz80yRXnnYsWUCMUwMLbW6FiWsRDHfcnRnLnIzHshlwtSagdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('1c0acc58dac713e55ac553c27f538350')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
    time = dt2.strftime("%H:%M:%S")
    now = int(dt2.strftime("%H"))*60 + int(dt2.strftime("%M"))
    day = dt2.strftime("%D")
    # 各群組的資訊互相獨立
    try:
        groupID = event.source.group_id
    except: # 此機器人設計給群組回報，單兵不可直接一對一回報給機器人
        message = TextSendMessage(text='我只接收群組內訊息，請先把我邀請到群組!')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        if not reportData.get(groupID): # 如果此群組為新加入，會創立一個新的儲存區
            reportData[groupID]={'time':[], '開始回報':1 ,'reported':[], 'day':day, 'clock':set()}
        if reportData[groupID]['clock']:
            reportData[groupID]['notify'] = list(reportData[groupID]['clock'])[0]
        if not day == reportData[groupID]['day']:
            reportData[groupID]['day'] = day
            reportData[groupID]['reported'] = []
        if not reportData[groupID]['notify']:
            reportData[groupID]['notify'] = 999999
        notify = reportData[groupID]["notify"]
#         notify = reportData[groupID]['notify']
        if (now in range(notify, notify+5)) and reportData[groupID]["開始回報"]:
            num = [i for i in reportData[groupID].keys() if isinstance(i, int)]
            for data in [reportData[groupID][number] for number in sorted(num)]:
                LineMessage = LineMessage + data[notify] +'\n\n'
            reportData[groupID]['reported'].append(notify)
            reportData[groupID]['clock'] = set(reportData[groupID]['time'] ) - set(reportData[groupID]['reported'])
                
        
#         if time[:-3] in reportData[groupID]['time'] and reportData[groupID]['開始回報'] and time[:-3] not in reportData[groupID]['reported'] :
#             try:
#                 reportData[groupID]['reported'].append(time[:-3])
#                 num =[i for i in reportData[groupID].keys() if isinstance(i, int)]
#                 for data in [reportData[groupID][number] for number in sorted(num)]:
#                     LineMessage = LineMessage + data[time[:-3]] +'\n\n'
# #                     message = TextSendMessage(text=data[time[:-3]])
# #                     line_bot_api.reply_message(event.reply_token, message)
#             except BaseException as err:
#                 LineMessage = '錯誤原因: '+str(err)
            
            
        LineMessage = ''
        receivedmsg = event.message.text
        if '建立資料' in receivedmsg and '姓名' in receivedmsg and '學號' in receivedmsg and '手機' in receivedmsg:
            try:
                if ( # 檢查資料是否有填，字數注意有換行符
                    len(receivedmsg.split('姓名')[-1].split('學號')[0])<3 and
                    len(receivedmsg.split("學號")[-1].split('手機')[0])<3 and 
                    len(receivedmsg.split('手機')[-1].split('地點')[0])<12
                    ):
                    raise Exception
                # 得到學號
                tprt = str(36+random.randint(0, 9)*0.1)
                ID = receivedmsg.split("學號")[-1].split('手機')[0][1:]
                # 直接完整save學號 -Garrett, 2021.01.28  
                ID = int(ID)
               
            except Exception:
                LineMessage = '姓名、學號、手機，其中一項未填。'    
            else:
#                 reportData[groupID][ID] = receivedmsg
                reportData[groupID][ID] = {'msg':''}
                reportData[groupID][ID]['msg'] = receivedmsg.split('建立資料\n')[-1] +'\n體溫:36.'+str(random.randint(0, 9))
#                 reportData[groupID][ID]['data']

                LineMessage = str(ID)+'號弟兄，成功建立資料庫。'

        if '筆記使用說明' in receivedmsg and len(receivedmsg)==6:
            LineMessage = (
                '收到以下正確格式\n'
                '才會正確記錄。\n'
                '----------\n'
                '建立資料\n'
                '姓名：\n'
                '學號：\n'
                '手機：\n'
                '(防疫期間會自動加入體溫)'
                '----------\n'
                '\n'
                '指令\n' 
                '----------\n'   
                '•設定回報時間\n'
                '->設定回報時間。\n'
                '->格式: \n'
                '->設定回報時間 \n'
                '->學號:XXX \n'
                '->設定時間:XX:XX:XX \n'
                '->其餘內容 \n'
                '->XXX:XXXXX \n'
                '•顯示回報時間\n'
                '->顯示回報時間\n'
                '•資料統計\n'
                '->顯示自動回報號碼。\n'
                '•開始回報\n'
                '->開始自動回報。\n'
                '•關閉回報\n'
                '->關閉自動回報。\n'
                '•手動回報\n'
                '->手動回報。\n'
                '->選擇時間:XX:XX。\n'
                '•清除資料\n'
                '->清空Data。\n'
                '----------\n' 
            )
        if '設定回報時間' in receivedmsg and '設定時間' in receivedmsg and '其餘內容' in receivedmsg:
            try:
                settime = receivedmsg.split('設定時間')[-1][1:9]
                nsettime = int(settime[:2])*60+int(settime[3:5])
                ID = receivedmsg.split("學號")[-1].split('設定時間')[0][1:]
                ID = int(ID)
                msg =  receivedmsg.split("其餘內容\n")[-1]
                reportData[groupID][ID][nsettime] = reportData[groupID][ID]['msg'] + '\n' + msg
                reportData[groupID]['time'].append(nsettime)
                reportData[groupID]['time'] = sorted(reportData[groupID]['time'])
                if nsettime < now:
                    reportData[groupID]['reported'].append(nsettime)
                reportData[groupID]['clock'] = set(reportData[groupID]['time'] ) - set(reportData[groupID]['reported'])
                LineMessage = str(ID)+'號弟兄,已設定時間:' + settime[:-3] 
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)
#         elif '設定回報時間' in receivedmsg and '設定時間' in receivedmsg and '其餘內容' in receivedmsg:
#             time = receivedmsg.split('設定時間')[-1][1:9]
#             ID = receivedmsg.split("學號")[-1].split('設定時間')[0][1:]
#             ID = int(ID)
#             msg =  receivedmsg.split("其餘內容\n")[-1]
#             reportData[groupID][ID][time[:-3]] = reportData[groupID][ID]['msg'] + '\n' + msg
#             reportData[groupID]['time'].append(time[:-3])
#             LineMessage = str(ID)+'號弟兄,已設定時間:' + time[:-3] 
        if '開始回報' in receivedmsg and len(receivedmsg)==4:
            reportData[groupID]["開始回報"]=1
            LineMessage = "開始自動回報"
        if '關閉回報' in receivedmsg and len(receivedmsg)==4:
            reportData[groupID]["開始回報"]=0
            LineMessage = "關閉自動回報"
        
        if '手動回報' in receivedmsg and '選擇時間' in receivedmsg:
            t = receivedmsg.split('選擇時間')[-1][1:6]
            t = int(t[:2])*60 + int(t[3:5])
            num =[i for i in reportData[groupID].keys() if isinstance(i, int)]
            for data in [reportData[groupID][number] for number in sorted(num)]:
                LineMessage = LineMessage + data[t] +'\n\n'
#         elif '手動回報' in receivedmsg and '選擇時間' in receivedmsg:
#             #             try:
#             t = receivedmsg.split('選擇時間')[-1][1:6]
#             num =[i for i in reportData[groupID].keys() if isinstance(i, int)]
#             for data in [reportData[groupID][number] for number in sorted(num)]:
#                 LineMessage = LineMessage + data[t] +'\n\n'
# #                     message = TextSendMessage(text=data[t])
# #                     line_bot_api.reply_message(event.reply_token, message)
                    
# #             except BaseException as err:
# #                 LineMessage = '錯誤原因: '+str(err)
        if '顯示回報時間' in receivedmsg and len(receivedmsg)==6:
            LineMessage = '回報時間統計: '
            for i in reportData[groupID]['time']:
                t = str(i//60)+':'+str(i%60)
                LineMessage = LineMessage + t +'\n'
            
        if '清除資料' in receivedmsg and len(receivedmsg)==4:
#             reportData[groupID]['time'] = []
            reportData[groupID] = {'time':[], '開始回報':1,'reported':[], 'day':day, 'clock':set()}
#             for i in reportData[groupID].keys():
#                 for j in reportData[groupID][i].keys():
#                     if not j=='msg':
#                         reportData[groupID][i].pop(j, None)
            LineMessage = "已清除所有時間"
        if '現在時間' in receivedmsg and len(receivedmsg)==4:
            LineMessage = time
            
        if '資料統計' in receivedmsg and len(receivedmsg)==4:
            try:
                num =[i for i in reportData[groupID].keys() if isinstance(i, int)]
                LineMessage = (
                    '完成資料建立的號碼有:\n'
                    +str([number for number in sorted(num)]).strip('[]')
                )
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)
            
#         elif '輸出回報' in receivedmsg and len(receivedmsg)==4:
#             try:
#                 LineMessage = ''
#                 for data in [reportData[groupID][number] for number in sorted(reportData[groupID].keys())]:
#                     LineMessage = LineMessage + data +'\n\n'
#             except BaseException as err:
#                 LineMessage = '錯誤原因: '+str(err)
#             else:
#                 reportData[groupID].clear()

#         elif '格式' in receivedmsg and len(receivedmsg)==2:
#             LineMessage = '姓名：\n學號：\n手機：\n地點：\n收假方式：'
            
        # for Error Debug, Empty all data -Sophia_Chen, 2021.01.25        
#         elif '清空' in receivedmsg and len(receivedmsg)==2:
#             reportData[groupID].clear()
#             LineMessage = '資料已重置!'

        
        if LineMessage :
            message = TextSendMessage(text=LineMessage)
            line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    global reportData
#     fornt = {"姓名":"", "學號":"", "手機":"","地點":"","開始回報":0}
    reportData = {}
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
