from SQLPkg.CRUD import Landmark_CRUD

DB = 'landmark'

crud = Landmark_CRUD('azureuser')

crud.read(DB, DB, 'id', 'coordinate', 'name')




#id name contents homepage tel hour address coordinate
crud.insert(DB, DB, '3', '쉐ㅔㅔㅔㅔ엣', '대구 중심지에 위치한...', 'http://www....', '053-000-0000', '이용시간...', '대구광역시 ...', '[123.123123, 543.754374]')