import requests
from bs4 import BeautifulSoup
import json
import steam
from steam.steamid import SteamID

# in the future
# Разбор мутов/банов
# Обработка подобного:
# Exception
# Попробовать ввод этой строки в lineedit PyQT5
'''
30.07.2023 7:49:31	22		Иркутск	"хочу чтобы люди играть спокойно ,без читеров и токсичных людей,и буду стараться уделять этому максимальное время
 "	https://steamcommunity.com/profiles/76561199103129825/	https://vk.com/weyliayame	tronnek	https://forum.zubat.ru/index.php?/profile/784-todimaks/	warloc2020@mail.ru	2,859 ч 3 ч мало часов на серверах	Fen1x
'''


def key_check():
    global KEY
    with open('key.txt', 'r', encoding='utf-8') as file:
        KEY = file.readline()
        if '\n' in KEY:
            KEY = KEY[:-1]
    if KEY == '':
        return False
    else:
        return True


def add_key(key: str):
    with open('key.txt', 'w', encoding='utf-8') as file:
        file.write(key)
    print(f'Ключ {key} успешно добавлен')


def check_ban_mute(steamid):
    try:
        mute_url = f'https://sb.zubat.ru/index.php?p=commslist&advSearch={steamid}&advType=steamid'
        ban_url = f'https://sb.zubat.ru/index.php?p=banlist&advSearch={steamid}&advType=steamid'
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


def find_info(url):
    try:
        id64 = SteamID(steam.steamid.steam64_from_url(url))
        id = id64.as_steam2
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

    return id, id64, is_private, nickname, profile_link


def get_info():
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
        print('Ошибка при парсинге информации.')
        return None

    try:
        id, id64, is_private, nickname, profile_link = find_info(url)
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

    check_ban_mute(id)

    print(f'\nСсылка на профиль - {profile_link}\n'
          f'Steam id пользователя - {id}\n'
          f'ID64 - {id64}\n'
          f'Приватность профиля - {"Скрыт" if is_private else "Открыт"}\n'
          f'Ник - {nickname}\n'
          f'Ник на форуме - {forum_nickname}\n'
          f'Наигранное время на аккаунте - {str(total_time_played)}\n')


def main():
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
