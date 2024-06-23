# -*- coding: UTF-8 -*-

#Python module requirement: line-bot-sdk, flask
import env
import DAI
import DAN
import MsgDealer
import globalState
import threading
import time 
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage
line_bot_api = LineBotApi(env.ChannelAccessToken) #LineBot's Channel access token
handler = WebhookHandler(env.ChannelSecret)       #LineBot's Channel secret

user_id_set=set()                                         #LineBot's Friend's user id 
app = Flask(__name__)

def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None


def saveUserId(userId):
    idFile = open('idfile', 'a')
    idFile.write(userId+';')
    idFile.close()

@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    # print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    # if Msg == 'Hello, world': return
    # print('GotMsg:{}'.format(Msg))
    userId = event.source.user_id
    if not userId in user_id_set:
        user_id_set.add(userId)
        saveUserId(userId)
        
    reply_message = MsgDealer.PreMsgRouter(Msg, userId)
    reply_message = MsgDealer.FunctionRouter(reply_message)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_message))   # Reply API example

    
#     db.session.add(user_message)
#     db.session.commit()
    # user_message = UserMessage(user_id=userId, message=Msg)
    # db.session.add(user_message)
    # db.session.commit()

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linebot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
    
class UserMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)

def siren_loop():
    while True:
        if globalState.SIREN_SIG:
            DAI.pushIDF('siren_idf', 1)
        time.sleep(1)  # Sleep to simulate work and avoid CPU overuse
        
def send_msg_loop(userId):
    while True:
        if globalState.SIREN_SIG: 
            flag = DAN.pull('2_odf')
            if flag != None:
                if int(flag[0]) == 100: 
                    c = datetime.now()
                    current_time = c.strftime('%H:%M:%S')
                    msg = '有人在' + current_time + '時意圖開啟房門'
                    line_bot_api.push_message(userId, TextSendMessage(text=msg))
                    time.sleep(5)


if __name__ == "__main__":
    globalState.initialize()
    idList = loadUserId()
    threads = []
    loop_thread1 = threading.Thread(target=siren_loop, daemon=True)
    loop_thread1.start()
    threads.append(loop_thread1)
    
    if idList: user_id_set = set(idList)
    try:
        for i, userId in enumerate(user_id_set):
            line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
            thread = threading.Thread(target=send_msg_loop, args=(userId,), daemon = True )
            threads.append(thread)
            thread.start()
    except Exception as e:
        print(f"An error occurred: {e}")
        for t in threads:
            t.join()
    
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

