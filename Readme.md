Python vers >= 3.8<br>
Проект предназначен для ускоренной проверки пользователей из заявок на админ-роль проекта zubat.ru<br>
Подразумевается работа в консоли.<br>
======================================<br>
<b>Инструкция по использованию:</b><br>
1) Склонировать проект с помощью <code>git clone github.com/S3raphimCS/zubat_admin_check</code> (Для этого в системе должен быть установлен git)<br>
2) Создать в папке виртуальное окружение с помощью команды <code>python -m venv venv</code><br>
3) Активировать виртуальное окружение командой <b>Windows</b>: <code>venv\scripts\activate</code> <b>Linux</b>: <code>source venv/bin/activate</code><br>
4) Скачать необходимые библиотеки командой <code>pip install -r requirements.txt</code>
5) Получить ключ Steam API по <a href='https://steamcommunity.com/dev'>этой ссылке</a> <br>
6) В папке проекта создать файл <code>.env</code> и добавить в него переменную STEAM_KEY со значением, которое было получено во втором пункте. <b>Пример</b>: <code>STEAM_KEY=123</code><br>
7) Запустить файл <code>main.py</code>  
