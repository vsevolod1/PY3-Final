from urllib.parse import urlencode, urlparse
import requests
import time
import json
from pprint import pprint

# Получение токена
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
    token = config['TOKEN']
    print('Токен из файла получен')
except Exception:
    print('Токен получить не удалось')
    exit()

VERSION = '5.64'
VK_API_PATH = 'https://api.vk.com/method/'
COMMON_PARAMS = {'access_token': token, 'v': VERSION, }

# Функция получения списка друзей
def get_user_friends(user_id=None):
    params = {'user_id': user_id}
    params.update(COMMON_PARAMS)
    response = requests.get(VK_API_PATH + 'friends.get', params)
    print('Список друзей пользователя получен')
    return response.json()['response']['items']

# Функция получения групп друзей
def get_user_groups(user_id=None, extended='1'):
    params = {"user_id": user_id, "extended": extended, 'fields': 'members_count'}
    params.update(COMMON_PARAMS)
    response = requests.get(VK_API_PATH + 'groups.get', params)
    print('Список групп пользователя получен')
    return response.json()['response']['items']

# Функция групповой проверки пользователей
def is_member_group (user_list, group_id):
    ul = [str(i) for i in user_list]
    str_list = (',').join(ul)
    params = {"user_ids": str_list, "group_id": group_id}
    params.update(COMMON_PARAMS)
    response = requests.get(VK_API_PATH + 'groups.isMember', params)
    return response.json()['response']

# Функция получения списка групп, в которых никто не состоит, кроме указанного пользователя
def get_secret_groups(user_list, user_groups):
    # Разбивка большого количества пользователей на пачки по 350 (больше не проходило)
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
        for lst in list_user_list:
            group_users_info += is_member_group(lst, group['id'])

        # увеличение счетчика
        for group_user in group_users_info:
            group['friends'] += group_user['member']

        # если друзей в группе нет, добавляем ее в список
        if group['friends'] == 0:
            print('В группе {} никто не состоит'.format(group['name']))
            group_info = {'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']}
            secret_groups.append(group_info)
        else:
            print('Группа {} не секретна'.format(group['name']))
        time.sleep(1)
    return secret_groups

def main():
    # Получение id пользователя
    user_id = input('Введите id пользователя vk: ')

    # Получение друзей и групп пользователя
    user_list = get_user_friends(user_id)
    user_groups = get_user_groups(user_id)
    secret_groups = get_secret_groups(user_list, user_groups)

    # Запись результата в json
    with open('groups.json', 'w', encoding='utf8') as outfile:
        json.dump(secret_groups, outfile, ensure_ascii=False)
        print('Данные о секретных группах выгружены в файл')

if __name__ == '__main__':
    main()
