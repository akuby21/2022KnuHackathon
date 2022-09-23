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
DB = 'landmark'
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
    global limit_landmark_distance, can_go_landmark
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
    new_can_go[pid] = []
    for i in coordinates:
        if cal_distance(current_pos, i) < limit_landmark_distance:
            new_can_go[pid].append(i)
    if new_can_go[pid] != can_go_landmark[pid]:
        if new_can_go[pid] == []:
            bot.send_message(chat_id=id, text="NO WHERE TO GO")
        else:    
            bot.send_message(chat_id=id, text=new_can_go[pid])
    can_go_landmark[pid] = copy.deepcopy(new_can_go[pid])
    
    
crud = Landmark_CRUD('azureuser')
print(crud.read(DB,DB,'id','coordinate','name'))
echo_handler = MessageHandler(Filters.text, handler)
location_handler = MessageHandler(Filters.location, location)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(location_handler)


