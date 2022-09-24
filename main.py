from SQLPkg.CRUD import Landmark_CRUD
import telegram
import psycopg2
import json
import os
import glob
#import googlemaps
import numpy as np
import math
import copy
from telegram import Update, Bot
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram.ext import MessageHandler, Filters
import time
from decimal import *

gApi = ""
token = ''
limit_landmark_distance = 0.0005
can_go_landmark = []
new_can_go = []
bot = telegram.Bot(token)
SCHEMA = 'landmark'
TABLE = 'place'
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
path = "./User_Data/*.json"
[os.remove(f) for f in glob.glob(path)]
updater.start_polling()
crud = Landmark_CRUD('azureuser')

getcontext().prec = 10

def handler(update: Update, context:CallbackContext):
    id = update.message.chat_id
    user_text = update.message.text
    print(f'{id} : {user_text}')
    bot.send_message(chat_id=id, text="랜드마크 알림이를 사용하려면 실시간 위치 전송을 켜주세요")

def cal_distance(start,end):
    a = start[0]- end[0]
    b = start[1]- end[1]
    res = a*a + b*b
    return abs(res)


def location(update:Update, context:CallbackContext):
    global limit_landmark_distance
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    
    current_pos = (Decimal(message.location.latitude), Decimal(message.location.longitude))
    id = message.chat.id
    
    data = crud.read(SCHEMA,TABLE,'id','coordinate')
    new_can_go = [] # 랜드마크 ID

    idDistance = []

    # 현재 위치에서 갈 수 있는 랜드마크를 new_can_go에 저장
    for i in data:
        distance = cal_distance(current_pos, i[1])
        if  distance < limit_landmark_distance:
            idDistance.append(tuple([i[0], distance]))
    idDistance.sort(key = lambda x : x[1])
    
    for a in idDistance[:5]:
        new_can_go.append(a[0])
    
    #can_go_landmark json파일 불러오기

    try:
        with open(f"./User_Data/{id}.json",'r') as outfile:
            userLandData = json.load(outfile)['Landmark']
    except:
        userLandData = []
    print(f'{id} : {new_can_go} ({len(new_can_go)}/{len(idDistance)})')
    # 새로 갈 수 있는 랜드마크와 기존에 갈 수 있는 랜드마크가 다르고
    if set(new_can_go) != set(userLandData): # set 비교
        # 갈 곳 없으면 "NO WHERE TO GO", 갈 곳 있으면 새로운 장소
        if set(new_can_go) == set(): #비었으면
            print(f"{id} : NOWHERE TO GO")
            bot.send_message(chat_id=id, text="NOWHERE TO GO")
        else:
            for landmarks in new_can_go:
                newText = ''
                datas = crud.execute(f"SELECT name, contents, homepage, tel, hour, address FROM {SCHEMA}.{TABLE} WHERE id = {landmarks}",True)
                for data in datas:
                    newText = '\n\n'.join(data)
                bot.send_message(chat_id=id, text=newText)
    
    # 기존 갈 수 있는 장소 업데이트
    # json write
    with open(f"./User_Data/{id}.json",'w') as outfile:
        json.dump({'id':id,'Landmark':new_can_go},outfile)
    
    
echo_handler = MessageHandler(Filters.text, handler)
location_handler = MessageHandler(Filters.location, location)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(location_handler)

