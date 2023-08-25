# S3raphimCS 08.2023 Script for Zubat.ru
import requests
from bs4 import BeautifulSoup
import json
import steam
from steam.steamid import SteamID
from os.path import exists
from os import getenv

# На вход работы скрипта идет строка из таблицы google.
# Далее из нее парсятся нужные ссылки и с помощью реквестов и API стима выдается информацию о пользователе.

def check_url(url):
    '''Функция проверки ссылки.

    Простая проверка на валидность ссылки стим-аккаунта.
    '''
    if id64 := SteamID(steam.steamid.steam64_from_url(url)):
        if requests.get(f'https://zubat.ru/api/get_info?steam_id={id64}').status_code == 200:
            return (True, True)
        else:
            return (True, False)
    else:
        return False


def get_stat(profile):
    '''Функция для получения статистики аккаунта.

    Обращаясь к API зубата, получает словарь, в котором хранятся значения, возвращаемые пользователю в зависимости
    от переданного аргумента attr.
    "general" - Общая статистика.
    "public", "awp", "retake", "dm" - для соответствующих режимов.
    '''
    try:
        id64 = SteamID(steam.steamid.steam64_from_url(profile))
        zubat = json.loads(requests.get(f'https://zubat.ru/api/get_info?steam_id={id64}').text)
    except json.decoder.JSONDecodeError:
        '''Аккаунт не имеет статистики на проекте'''
        return 'Ваш аккаунт не зарегистрирован на нашем проекте.'

        '''
        Возвращает статистику по конкретному режиму, переданному в функцию в параметре attr
        Возможные аргументы - "awp", "public", "retake", "dm"
        '''
        awp_time = round(zubat['user_stats'][0]['awp_playtime'] / 60 / 60, 1)
        public_time = round(zubat['user_stats'][0]['public_playtime'] / 60 / 60, 1)
        dm_time = round(zubat['user_stats'][0]['dm_playtime'] / 60 / 60, 1)
        retake_time = round(zubat['user_stats'][0]['retake_playtime'] / 60 / 60, 1)
        return {'awp': awp_time,
                'public_time': public_time,
                'dm_time': dm_time,
                'retake_time': retake_time,
                'general_time': awp_time+public_time+dm_time+retake_time}


# Функция проверяет наличия API-ключа в файле key.txt
def key_check() -> bool:
    global KEY
    KEY = getenv('STEAM_KEY')
    if KEY:
        return True
    else:
        return False


# Функция добавляет введенный API-ключ в файл key.txt для последующего использования
def add_key(key: str) -> None:
    with open('key.txt', 'w', encoding='utf-8') as file:
        file.write(key)
    print(f'Ключ {key} успешно добавлен')


# Проверяет наличие банов и мутов у пользователя с переданным id на sb.zubat.ru
def check_ban_mute(steamid: str) -> None:
    try:
        mute_url = f'https://sb.zubat.ru/index.php?p=commslist&advSearch={steamid}&advType=steam'
        ban_url = f'https://sb.zubat.ru/index.php?p=banlist&advSearch={steamid}&advType=steam'
        mute_soup = BeautifulSoup(requests.get(mute_url).text, 'lxml')
        ban_soup = BeautifulSoup(requests.get(ban_url).text, 'lxml')
        number_of_mutes = int(mute_soup.find('div', {'class': 'card-body'}).find('p').text.split()[-1])
        number_of_bans = int(ban_soup.find('div', {'class': 'card-body'}).find('p').text.split()[-1])

        # Разбор мутов. (in the future)
        mutes = mute_soup.find('div', {'id': 'banlist'}).find('table')

        if number_of_bans or number_of_mutes:
            print(f'\nУказанный пользователь получал наказания ранее: \nБанов - {number_of_bans}\nМутов - {number_of_mutes}')
        else:
            print('\nПользователь не получал наказаний.')
    except Exception as excp:
        print('\nОшибка: ', excp)
        print('Ошибка проверки пользователя на баны/муты')


# Получает на вход ссылку на steam-профиль пользователя
# Возвращает id64, steam_id, статус приватности профиля, ник в стиме и на форуме, айди для поиска по банам пользователя.
def find_info(url: str) -> (str, str, bool, str, str, str):
    try:
        id64 = SteamID(steam.steamid.steam64_from_url(url))
        if not id64:
            raise ValueError
        id = id64.as_steam2
        id_for_bans = id.split(':')[-1]
        account_request = json.loads(requests.get(
            f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={KEY}&steamids={id64}').text)[
            'response']['players'][0]
        private_status = {
            1: True,
            3: False,
        }
        is_private = private_status[account_request['communityvisibilitystate']]
        nickname = account_request['personaname']
        profile_link = f'http://steamcommunity.com/profiles/{id64}'
    except:
        return 'Ошибка получения инфорамации о пользователе'

    return id, id64, is_private, nickname, profile_link, id_for_bans


# Парсинг информации из строки таблицы и активация остальных функций
def get_info() -> None:
    try:
        info = input('Введите информацию из заявки: ')
        info = info.split('\t')
        while '' in info:
            info.remove('')
        info = [line.rstrip() for line in info]
        url = info[4]
        if 'steamcommunity' not in url:
            print('Неправильная стим-ссылка')
            return False
        forum_url = info[7]
        if 'forum.zubat.ru' in forum_url:
            bs = BeautifulSoup(requests.get(forum_url).text, 'lxml')
            forum_nickname = bs.find('div',
                                     {'class': 'ipsPos_left'}).find('h1').text
            forum_nickname = ''.join([letter for letter in list(forum_nickname) if letter.isalpha()])
        else:
            forum_nickname = 'Неверная ссылка на форум'

    except:
        print('Ошибка при парсинге информации. Проверьте введенную информацию, возможно, ошибка в ней.')
        return False

    try:
        id, id64, is_private, nickname, profile_link, id_for_bans = find_info(url)
        hours = json.loads(requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={KEY}&steamid={id64}&format=json').text)
        try:
            if not is_private:
                for game in hours['response']['games']:
                    if game['appid'] == 730:
                        total_time_played = int(game['playtime_forever'] / 60)
                        break
                else:
                    total_time_played = 0
        except KeyError:
            total_time_played = 'Закрыт доступ к просмотру игр'

    except Exception as excp:
        print("Ошибка: ", excp)
        print('Ошибка при попытке получения общей информации о странице.')
        return None

    check_ban_mute(id_for_bans)

    print(f'\nСсылка на профиль - {profile_link}\n'
          f'Steam id пользователя - {id}\n'
          f'ID64 - {id64}\n'
          f'Приватность профиля - {"Скрыт" if is_private else "Открыт"}\n'
          f'Ник - {nickname}\n'
          f'Ник на форуме - {forum_nickname}\n'
          f'Наигранное время на аккаунте - {str(total_time_played)}\n')


# Функция, запускающая цикл работы программы
def main() -> None:
    if not key_check():
        print("Внимание!!! Не обнаружено файла с ключом.\n"
              "Steam API key можно получить по ссылке - https://steamcommunity.com/dev/apikey")
    while True:
        print(f'1. Добавить/Изменить ключ steam API\n'
              f'2. Разбор заявки\n'
              f'3. Выход')
        choose = input('Введите пункт меню: ')
        if choose == '1':
            key = input('Введите ключ: ')
            add_key(key)
        elif choose == '2':
            if key_check():
                get_info()
            else:
                print('Нет API ключа.')
        elif choose == '3':
            break
        else:
            print('Вы ввели неправильное значение.')


if __name__ == '__main__':
    main()
