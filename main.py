import telebot
import time
import pandas as pd
import random as rd
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv('config.env')
users = pd.read_csv('users.csv')

OWNER_ID = os.getenv('OWNER_ID')
USER_ID = os.getenv('USER_ID')
AUTO_MODE = True
TOKEN = os.getenv('TOKEN')
ANSWERS = ['Ок', 'Да', 'Нет', 'Ок', 'Хорошо', 'Прикольно', 'Ахахахахах']

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(
    func=lambda message: str(message.from_user.id) not in users['user_id'].astype(
        str).tolist(), commands=['start'])
def start(message):
    try:
        users.loc[len(users)] = [message.chat.id, message.from_user.first_name]
        users.to_csv('users.csv', index=False)
        print(f'Пользователь {message.from_user.first_name} добавлен с ID: {message.chat.id}')
        bot.reply_to(message, f'Приветсвую вас, {message.from_user.first_name}!')
    except:
        bot.reply_to(message, 'Ошибка, попробуйте ещё раз')
        print('Ошибка при добавлении пользователя')


@bot.message_handler(func=lambda message: (message.from_user.id == int(OWNER_ID)) and message.text.startswith('/'),
                     content_types=['text'])
def owner_commands(message):
    if message.text.startswith('/add'):
        user_data = message.text.split()[1:]
        if len(user_data) == 2:
            user_id, user_name = user_data
            users.loc[len(users)] = [user_id, user_name]
            users.to_csv('users.csv', index=False)
            bot.reply_to(message, f'Пользователь {user_name} добавлен с ID: {user_id}')
        else:
            bot.reply_to(message, 'Неверный формат команды. Используйте: /add <user_id> <user_name>')

    elif message.text.startswith('/list'):
        user_list = '\n'.join([f'{row["user_name"]} - {row["user_id"]}' for _, row in users.iterrows()])
        bot.reply_to(message, f'Список пользователей:\n{user_list}')

    elif message.text.startswith('/set'):
        try:
            user_name = message.text.split()[1]
            user_row = users[users['user_name'] == user_name]
            if not user_row.empty:
                global USER_ID
                USER_ID = user_row.iloc[0]['user_id']
                bot.reply_to(message, f'Пользователь для общения установлен: {user_name} (ID: {USER_ID})')
            else:
                bot.reply_to(message, 'Пользователь с таким именем не найд=ен.')
        except:
            bot.reply_to(message, 'Команда должна иметь формат /set <Имя пользователя>')

    elif message.text.startswith('/id'):
        bot.reply_to(message, f'Текущий пользователь для общения: {USER_ID}')

    elif message.text.startswith('/help'):
        bot.reply_to(message, """
                                    Список команд:\n
                                    /add <user_id> <user_name> - добавить пользователя\n
                                    /list - вывести список пользователей\n
                                    /set <Имя пользователя> - начать общение с выбранным пользователем\n
                                    /id - узнать с каким пользователем ведётся общение\n
                                    /auto - включить/выключить режим авто-ответа
                                    """)

    elif message.text.startswith('/auto'):
        global AUTO_MODE
        AUTO_MODE = not AUTO_MODE
        if AUTO_MODE:
            bot.reply_to(message, 'Режим авто-ответа включен')
        else:
            bot.reply_to(message, 'Режим авто-ответа выключен')

    else:
        bot.send_message(OWNER_ID, 'Неизвестная команда')


@bot.message_handler(func=lambda message: (message.from_user.id == int(OWNER_ID)), content_types=['text'])
def send_message_to_user(message):
    if not AUTO_MODE:
        try:
            user_name = users.loc[users['user_id'].astype(str) == str(USER_ID), 'user_name'].values[0]
            current_time = datetime.now().strftime("%H:%M")
            bot.send_message(USER_ID, message.text)
            print(f'[{current_time}] Светлана проводник to {user_name}: {message.text}')
        except:
            print('Ошибка при отправке сообщения')


@bot.message_handler(func=lambda message: str(message.from_user.id) in users['user_id'].astype(str).tolist(),
                     content_types=['text'])
def get_message_from_users(message):
    current_time = datetime.now().strftime("%H:%M")
    user_name = users.loc[users['user_id'].astype(str) == str(message.from_user.id), 'user_name'].values[0]
    print(f'[{current_time}] {user_name}: {message.text}')
    if AUTO_MODE:
        try:
            bot.send_chat_action(chat_id=message.chat.id, action='typing')
            message_index = rd.randint(0, len(ANSWERS) - 1)
            message_text = ANSWERS[message_index]
            time.sleep(rd.randint(1, 3))
            bot.send_message(message.chat.id, message_text)
            print(f'[{current_time}] Светалана проводник: {message_text}')
        except:
            print('Ошибка при отправке сообщения')


bot.infinity_polling()
