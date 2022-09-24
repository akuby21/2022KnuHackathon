from SQLPkg.CRUD import Landmark_CRUD
import telegram
import psycopg2
#import googlemaps
import numpy as np
import math
import copy
from telegram import Update, Bot
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram.ext import MessageHandler, Filters
import time
USERNUMBER = 10

gApi = ""
token = ''
limit_landmark_distance = 0.01
can_go_landmark = [[0 for col in range(USERNUMBER)] for row in range(99)]
new_can_go = [[0 for col in range(USERNUMBER)] for row in range(99)]
bot = telegram.Bot(token)
SCHEMA = 'landmark'
TABLE = 'place'
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

updater.start_polling()

def handler(update: Update, context:CallbackContext):
    id = update.message.chat_id
    user_text = update.message.text
    print(f'{id} : {user_text}')
    bot.send_message(chat_id=id, text="랜드마크 알림이를 사용하려면 실시간 위치 전송을 켜주세요")

def cal_distance(start,end):
   res = math.sqrt(math.pow(start[0]-end[0],2)+math.pow(start[1]-end[1],2))
   return abs(res)


def location(update:Update, context:CallbackContext):
    global limit_landmark_distance
    print(f'>> {update}')
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    
    current_pos = (message.location.latitude, message.location.longitude)
    id = message.chat.id
    print(f'{id} : {current_pos}')
    pid = id % 50
    coordinates = [[35.867576, 128.6245084],[35.8605323, 128.5599617],[37.5384272, 126.9654442],[35.867808, 128.624797],[35,128],[35.8674923, 128.6242198], [35.8605201, 128.5598575]]
    
    new_can_go = [] # 랜드마크 ID

    # 현재 위치에서 갈 수 있는 랜드마크를 new_can_go에 저장
    for i in coordinates:
        if cal_distance(current_pos, i) < limit_landmark_distance:
            new_can_go[pid].append(i)
    
    #can_go_landmark json파일 불러오기
    # ...

    # 새로 갈 수 있는 랜드마크와 기존에 갈 수 있는 랜드마크가 다르고
    if set(new_can_go) != set(can_go_landmark): # set 비교
        # 갈 곳 없으면 "NO WHERE TO GO", 갈 곳 있으면 새로운 장소
        if set(new_can_go) == set(): #비었으면
            bot.send_message(chat_id=id, text="NO WHERE TO GO")
        else:
            bot.send_message(chat_id=id, text=new_can_go[pid])
    
    # 기존 갈 수 있는 장소 업데이트
    # json write
    can_go_landmark = copy.deepcopy(new_can_go)
    
    
crud = Landmark_CRUD('azureuser')
data = crud.read(SCHEMA,TABLE,'id','coordinate','name')
print(data[-1])
echo_handler = MessageHandler(Filters.text, handler)
location_handler = MessageHandler(Filters.location, location)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(location_handler)


