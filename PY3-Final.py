from urllib.parse import urlencode, urlparse
import requests
import time
import json
from pprint import pprint

# Функция получения списка друзей
def get_user_friends(user_id = None):
    params['user_id'] = user_id
    response = requests.get('https://api.vk.com/method/friends.get', params)
    return response.json()['response']['items']

# Функция получения групп друзей
def get_user_groups(user_id = None, extended = '0'):
    params['user_id'] = user_id
    params['extended'] = extended
    response = requests.get('https://api.vk.com/method/groups.get', params)
    return response.json()['response']['items']

# Функция групповой проверки пользователей
def is_member_group (user_list, group_id):
#     str_list = [str(i) for i in user_list]
#     params['user_ids'] = (',').join(str_list)
    ul = [str(i) for i in user_list]
#     pprint(ul)
    str_list = (',').join(ul)
    params['user_ids'] = str_list
    params['group_id'] = group_id
    response = requests.get('https://api.vk.com/method/groups.isMember', params)
    return response.json()['response']


VERSION = '5.64'
TOKEN = ''
# TOKEN = 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22'

# Получение токена
try:
    token_file = "token.json"
    with open(token_file) as tf:
        TOKEN = tf.read()
    print('Токен из файла получен')
except BaseException:
    print('Токен получить не удалось')

params = {'access_token': TOKEN,
          'v': VERSION, }

# Получение id пользователя
USER_ID = input('Введите id пользователя vk: ')
# USER_ID = '5030613'

# Получение друзей и групп пользователя
user_list = get_user_friends(USER_ID)
print('Список друзей пользователя получен')
user_groups = get_user_groups(USER_ID, '1')
print('Список групп пользователя получен')

# Разбивка большого количества пользователей на пачки по 350 (больше не проходило)
if len(user_list) > 350:
    list_user_list = [user_list[i:i + 350] for i in range(0, len(user_list), 350)]

# Проверка групп на наличие друзей
print('Проверка групп на наличие друзей')
# список групп, в которых не состоят друзья
secret_groups = []
for group in user_groups:
    # счетчик количества друзей в группе
    group['friends'] = 0
    group_users_info = []

    # проверка пользователей на наличие в группе (списком из списков или единым списком, если менее 350)
    if list_user_list:
        for lst in list_user_list:
            group_users_info += is_member_group(lst, group['id'])
    else:
        group_users_info = is_member_group(user_list, group['id'])

    # увеличение счетчика
    for group_user in group_users_info:
        group['friends'] += group_user['member']

    # если друзей в группе нет, добавляем ее в список
    if group['friends'] == 0:
        print('В группе {} никто не состоит'.format(group['name']))
        secret_groups += group
    else:
        print('Группа {} не секретна'.format(group['name']))
    time.sleep(1)

# Запись результата в json
with open('groups.json', 'w', encoding='utf8') as outfile:
    json.dump(user_groups, outfile, ensure_ascii=False)
    print('Данные о секретных группах выгружены в файл')
