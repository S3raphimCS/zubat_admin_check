import requests
from bs4 import BeautifulSoup
import json

# Steam-key будет необходимо спрятать / Люди сами могут его получить на сайте стима *ссылка*
KEY = '4294B768A71D5E4655F3C5323B64B2CB'


# FIXME
'''
Переделать это под STEAM API через эту ссылку http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=XXXXXXXXXXXXXXXXXXXXXXX&steamids=XXXXXXXXXXXXX
Документация - https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_.28v0001.29
Раздел - GetPlayerSummaries
'''


def find_info(soup):
    try:
        print(soup.find('section',
                  {'class': 'panel-default'}))
        STEAM_ID = soup.find('section',
                             {'class': 'panel-default'}).find_all('dd',
                                                                  {'class': 'value'})[0].find('a').text
        STEAM_ID64 = soup.find('section',
                               {'class': 'panel-default'}).find_all('dd',
                                                                    {'class': 'value'})[2].find('a').text
        is_private = soup.find('section',
                               {'class': 'panel-default'}).find_all('dd',
                                                                    {'class': 'value'})[4].find('span').text == 'public'
        STEAM_NICKNAME = soup.find('section',
                                   {'class': 'panel-default'}).find_all('dd',
                                                                        {'class': 'value'})[6].text
        STEAM_PROFILE_LINK = soup.find('section',
                                       {'class': 'panel-default'}).find_all('dd',
                                                                            {'class': 'value'})[9].find('a').text.replace(' ', '').replace('\n', '')
        hours = json.loads(requests.get(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={KEY}&steamid={STEAM_ID64}&format=json').text)
        total_time_played = 0
    except IndexError:
        print(soup.find('section',
                             {'class': 'panel-default'}))
        STEAM_ID = soup.find('section',
                             {'class': 'panel-default'}).find_all('td')[1].find('code').text
        STEAM_ID64 = soup.find('section',
                               {'class': 'panel-default'}).find_all('td')[7].find('code').text
        print(STEAM_ID64)
        is_private = soup.find('section',
                               {'class': 'panel-default'}).find_all('td',
                                                                    {'class': 'value'})[4].find('span').text == 'public'
        STEAM_NICKNAME = soup.find('section',
                                   {'class': 'panel-default'}).find_all('td',
                                                                        {'class': 'value'})[6].text
        STEAM_PROFILE_LINK = soup.find('section',
                                       {'class': 'panel-default'}).find_all('td',
                                                                            {'class': 'value'})[9].find(
            'a').text.replace(' ', '').replace('\n', '')
        hours = json.loads(requests.get(
            f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={KEY}&steamid={STEAM_ID64}&format=json').text)
        total_time_played = 0

    print(STEAM_ID)
    return STEAM_ID, STEAM_ID64, is_private, STEAM_NICKNAME, STEAM_PROFILE_LINK, hours, total_time_played


def get_info():
    try:
        info = input('Введите информацию из заявки: ')
        info = info.split('\t')
        while '' in info:
            info.remove('')
        print(info)
        steam = info[4]
        id = steam.split('/')[-1]
        url = f'https://steamid.io/lookup/{id}'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
    except:
        print('Ошибка при попытке обращения к сервису получения информации о странице.')
        return None

    try:
        STEAM_ID, STEAM_ID64, is_private, STEAM_NICKNAME, STEAM_PROFILE_LINK, hours, total_time_played = find_info(soup)

        if not is_private:
            for game in hours['response']['games']:
                if game['appid'] == 730:
                    total_time_played = int(game['playtime_forever'] / 60)
                    break
            else:
                total_time_played = 0

    except Exception as excp:
        print(excp)
        print('Ошибка при попытке получения общей информации о странице.')
        return None

    print(STEAM_ID, STEAM_ID64, is_private, STEAM_NICKNAME, STEAM_PROFILE_LINK, total_time_played, end='\n')


def check_ban_mute(steamid):
    try:
        mute_url = f'https://sb.zubat.ru/index.php?p=commslist&advSearch={steamid}&advType=steamid'
        ban_url = f'https://sb.zubat.ru/index.php?p=banlist&advSearch={steamid}&advType=steamid'
        mute_soup = BeautifulSoup(requests.get(mute_url).text, 'lxml')
        ban_soup = BeautifulSoup(requests.get(ban_url).text, 'lxml')
        number_of_mutes = mute_soup.find('div', {'class': 'card-body'}).find('p').text.split()[-1]
        number_of_bans = ban_soup.find('div', {'class': 'card-body'}).find('p').text.split()[-1]
        if number_of_bans or number_of_mutes:
            print('У пользователя обнаружены полученные наказания.')
        else:
            print('Пользователь не получал наказаний.')
    except:
        print('Ошибка проверки пользователя на баны/муты')


def main():
    pass


if __name__ == '__main__':
    get_info()
