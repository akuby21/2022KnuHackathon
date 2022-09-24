import  json, os, glob
from    SQLPkg.CRUD     import Landmark_CRUD
from    decimal         import *


import  telegram
from    telegram        import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction,      Update,  Bot
from    telegram.ext    import CallbackQueryHandler, CallbackContext,      MessageHandler,  Updater, Filters

# PostgreSQL Constant
SCHEMA = 'landmark'
TABLE = 'place'

# Telegram Bot Constant
TOKEN = ''
VIEW_NUM = 5 #display #VIEW_NUM landmark only
LIMIT_DISTANCE = 0.0007

def start(update: Update, context:CallbackContext):
    # treat "/start" command

    id = update.message.chat_id
    user_text = update.message.text
    print(f'{id} : {user_text}')
    bot.send_message(chat_id=id, text="랜드마크 알림이를 사용하려면 실시간 위치 전송을 켜주세요")

def cal_distance(start,end):
    # calculate distance between two point

    a = start[0]- end[0]
    b = start[1]- end[1]
    res = a*a + b*b
    return abs(res)

def location(update: Update, context:CallbackContext):
    # get user location // display the landmark information // display the button for the navigation

    # message update
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    
    # get current coordinate
    current_pos = (Decimal(message.location.latitude), Decimal(message.location.longitude))
    id = message.chat.id

    new_can_go = [] # 랜드마크 ID list
    idDistance = [] # (id, distance) tuple list

    # 현재 위치에서 갈 수 있는 랜드마크를 new_can_go에 저장
    data = crud.read(SCHEMA,TABLE,'id','coordinate')
    for i in data:
        distance = cal_distance(current_pos, i[1])
        if  distance < LIMIT_DISTANCE:
            idDistance.append(tuple([i[0], distance]))
    idDistance.sort(key = lambda x : x[1])
    
    for a in idDistance[:VIEW_NUM]:
        new_can_go.append(a[0])

    # read user data
    try:
        with open(f"./User_Data/{id}.json",'r') as outfile:
            userLandData = json.load(outfile)['Landmark']
    except:
        userLandData = []
    print(f'{id} : {new_can_go} ({len(new_can_go)}/{len(idDistance)})')

    # 새로 갈 수 있는 랜드마크와 기존에 갈 수 있는 랜드마크가 다르고 or if new user
    if set(new_can_go) != set(userLandData) or not os.path.isfile(f'./User_Data/{id}.json'): # set 비교
        # 갈 곳 없으면 "NO WHERE TO GO", 갈 곳 있으면 새로운 장소
        if set(new_can_go) == set(): #비었으면
            print(f"{id} : NOWHERE TO GO")
            bot.send_message(chat_id=id, text="현재 위치에서 가까운 랜드마크가 없어요")
        else:
            new_can_go_name_VIEW_NUM = []
            for landmark_id in new_can_go:
                newText = ''
                datas = crud.execute(f"SELECT name, contents, homepage, tel, hour, address FROM {SCHEMA}.{TABLE} WHERE id = {landmark_id}",True)
                new_can_go_name_VIEW_NUM.append(datas[0][0])
                for data in datas:
                    newText = '\n\n'.join(data)

                # if isExit(photo) : send photo
                try:
                    bot.sendPhoto(chat_id=id, photo=open(f'./images/{landmark_id}.jpg','rb'), caption=newText)
                # else : send text only
                except:
                    bot.send_message(chat_id=id, text=newText)

            # display button
            task_buttons = [[]*(VIEW_NUM+1) for _ in range(VIEW_NUM+1)]
            for i, landmark_name in enumerate(new_can_go_name_VIEW_NUM):
                task_buttons[i].append(InlineKeyboardButton(f'{landmark_name}', callback_data=i))
            task_buttons[-1].append(InlineKeyboardButton('종료', callback_data=999))
            reply_markup = InlineKeyboardMarkup(task_buttons)

            bot.send_message(chat_id=id, text = "가고 싶은 장소 네비게이션 보기", reply_markup=reply_markup)

    # 기존 갈 수 있는 장소 업데이트
    with open(f"./User_Data/{id}.json",'w') as outfile:
        json.dump({'id':id,'Landmark':new_can_go,'Coordinate':[message.location.latitude,message.location.longitude]},outfile)

def run_button(update: Update, context:CallbackContext):
    # button click event

    query = update.callback_query
    button_number = int(query.data)
    id = query.message.chat_id              # user id
    message_id = query.message.message_id   # message id

    context.bot.send_chat_action(chat_id=id, action=ChatAction.TYPING)

    content = query.message.reply_markup.inline_keyboard

    if button_number == 999: # click "종료"
        context.bot.edit_message_text(chat_id=id, message_id=message_id, text='종료되었어요')
        os.remove(f'./User_Data/{id}.json')
    else:                    # click Landmark
        landmark_name = []
        with open(f"./User_Data/{id}.json",'r') as file:
            dep = json.load(file)['Coordinate']
        for data in content:
            landmark_name.append(data[0]['text'])
        dest = crud.execute(f"SELECT coordinate FROM {SCHEMA}.{TABLE} WHERE name = '{landmark_name[button_number]}'",True)
        dest = dest[0][0]

        # Google navigation URL
        href = f"https://google.co.kr/maps/dir/?api=1&origin={str(dep[0])},{str(dep[1])}&destination={str(dest[0])},{str(dest[1])}&travelmode=transit"
        context.bot.edit_message_text(chat_id=id, message_id=message_id, text=f"{landmark_name[button_number]}에 대한 네비게이션 정보에요\n{href}")

# Handler
start_handler = MessageHandler(Filters.text, start)
location_handler = MessageHandler(Filters.location, location)
button_handler = CallbackQueryHandler(run_button)

if __name__ == "__main__":
    # Telegram Bot initialize
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # User data file initialize
    [os.remove(f) for f in glob.glob("./User_Data/*.json")]

    # Telegram Bot Start
    updater.start_polling()
    bot = telegram.Bot(TOKEN)

    # PostgreSQL CRUD ready
    crud = Landmark_CRUD('azureuser')

    # decimal type precision range set
    getcontext().prec = 10

    # Dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(location_handler)
    dispatcher.add_handler(button_handler)