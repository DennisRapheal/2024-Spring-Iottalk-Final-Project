import DAI
import crawl
import env
import time
import globalState

def PreMsgRouter(msg, userId):
    if '冷氣加值'  == msg: 
        return AC_deposit()
    elif '天氣資訊'  == msg:
        return DormInfo()
    elif '啟用警報器' == msg: 
        return SirenActivate()
    elif '關閉警報器' == msg: 
        return SirenPulse()
    elif '關燈' == msg:
        return Lightoff()
    elif '開燈' == msg:
        return Lighton()
    else:
        return GPTreview(msg, userId)
    
def FunctionRouter(msg):
    if '冷氣加值' in msg: 
        return AC_deposit()
    elif '天氣資訊' in msg:
        return DormInfo()
    elif '啟用警報器' in msg: 
        return SirenActivate()
    elif '關閉警報器' in msg: 
        return SirenPulse()
    elif '開燈' in msg:
        return Lighton()
    elif '關燈' in msg:
        return Lightoff()
    elif '鎖門' in msg:
        return LockDoor()
    elif '解除門鎖' in msg:
        return UnlockDoor()
    else:
        return msg
        
def RepairRequest():
    return 'repairing'
    
def AC_deposit():
    return 'deposit'

def DormInfo():
    data = crawl.getdata()
    # for index, row in data.iterrows():  
    #     print(f"觀測時間: {str(row['觀測時間'])}\n \
    #     溫度: {str(row['溫度(°C)'])} \n\
    #     天氣: {str(row['天氣'])} \n \
    #     風向: {str(row['風向'])} \n \
    #     風力: {str(row['風力 (m/s)'])} \n\
    #     陣風: {str(row['陣風 (m/s)'])}  \n\
    #     能見度 : {str(row['能見度(公里)'])} \n\
    #     濕度: {str(row['相對溼度(%)'])} \n\
    #     氣壓: {str(row['海平面氣壓(百帕)'])} \n\
    #     累積雨量: {str(row['當日累積雨量(毫米)'])}\n\
    #     日照時數: {str(row['日照時數(小時)'])}")
    weather = str(data['天氣'][0])
    temp = str(data['溫度(°C)'][0])
    
    return '今天是 '+weather+' 天 現在溫度為：'+temp+'度'
    
def SirenActivate():
    globalState.SIREN_SIG = True
    return '已經為您開啟警報器'

def SirenPulse():
    globalState.SIREN_SIG = False
    DAI.pushIDF('siren_idf', 0)
    return '已經為您關閉警報器'

def Lighton():
    DAI.pushIDF('light_idf', 1)
    time.sleep(0.01)
    DAI.pushIDF('light_idf', 0)
    return '已經為您開燈'

def Lightoff():
    DAI.pushIDF('light_idf', -1)
    time.sleep(0.01)
    DAI.pushIDF('light_idf', 0)
    return '已經為您關燈'

def LockDoor():
    DAI.pushIDF('door_idf', 1)
    time.sleep(0.01)
    DAI.pushIDF('door_idf', 0)
    return '您的們已經上鎖'   
    
def UnlockDoor():
    DAI.pushIDF('door_idf', -1)
    time.sleep(0.01)
    DAI.pushIDF('door_idf', 0)
    return '已經解除門鎖'

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful dorm assistant. \
            You should first check out the following 6 points before replying any question: \
            1. If the question try to express their AC card is running out of money or they want to deposit, \
                top up the AV card,  you should only reply 冷氣加值\
            2. If the question try to get some information about the room or dorm, you should only reply 天氣資訊\
            3. If the question try to turn on the siren, you should only reply 啟用警報器\
            4. If the question try to turn off the siren, you should only reply 關閉警報器\
            5. If the question try to turn on the light , you should only reply 開燈\
            6. If the question try to turn off the light , you should only reply 關燈"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    max_tokens=50,
    timeout=None,
    max_retries=2,
    api_key=env.API_KEY
)
 
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: SQLChatMessageHistory(
        session_id=session_id, connection="sqlite:///sqlite.db"
    ),
    input_messages_key="question",
    history_messages_key="history",
)

def GPTreview(msg, userId):
    # This is where we configure the session id
    config = {"configurable": {"session_id": str(userId)}}
    reviewMsg =  chain_with_history.invoke({"question": msg}, config=config)
    print()
    print('AI_respond', reviewMsg.content)
    print()
    return reviewMsg.content
    
    