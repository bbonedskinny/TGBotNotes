import logging
import os
import pickle

import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name

    notes_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    add_notes = types.KeyboardButton(text='Добавить новую заметку')
    notes_markup.add(add_notes)

    view_notes = types.KeyboardButton(text='Посмотреть заметки')
    notes_markup.add(view_notes)

    find_notes = types.KeyboardButton(text='Поиск заметок')
    notes_markup.add(find_notes)

    delete_notes = types.KeyboardButton(text='Удалить заметку')
    notes_markup.add(delete_notes)

    save_data = types.KeyboardButton(text='Сохранить изменения')
    notes_markup.add(save_data)

    bot.send_message(chat_id, f'Привет, {first_name}! Я бот-замтека, создан для того, чтобы ты смог сохранять во мне '
                              f'свои самые скрытные и интересные мысли, обещаю, я никому не расскажу, '
                              f'быстрее нажимай на кнопки!', reply_markup=notes_markup)


@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    if message.chat.type == 'private':
        if message.text == 'Добавить новую заметку':
            new_note = bot.send_message(chat_id, f'Запишите Вашу новую заметку')
            bot.register_next_step_handler(new_note, save_notes)
        if message.text == 'Посмотреть заметки':
            view_note(message)
        if message.text == 'Поиск заметок':
            find_notes = bot.send_message(chat_id, f'Введите номер или слово из заметки, которую желаете найти')
            bot.register_next_step_handler(find_notes, find_note)
        if message.text == 'Удалить заметку':
            delete_notes = bot.send_message(chat_id, f'Введите номер заметки, которую желаете удалить')
            bot.register_next_step_handler(delete_notes, delete_note)
        if message.text == 'Сохранить изменения':
            saved_data(message)


data = {}

with open('saved_dictionary.pkl', 'rb') as f:
    loaded_data = pickle.load(f)
    if loaded_data:
        data = loaded_data


def save_notes(message):
    chat_id = message.chat.id
    if chat_id not in data:
        data[chat_id] = []
    data[chat_id].append(message.text)
    bot.send_message(chat_id, f'Заметка успешно сохранена')
    bot.send_message(chat_id, f'Не забудьте нажать на кнопку "Сохранить изменения", чтобы сохранить изменения')
    logging.info(message)


def view_note(message):
    chat_id = message.chat.id
    view = '\n'.join([str(index + 1) + '. ' + el for index, el in enumerate(data[chat_id])])
    view2 = f'Список ваших заметок: \n {view}'
    bot.send_message(chat_id, view2.lstrip())


def find_note(message):
    chat_id = message.chat.id
    num = message.text
    if num.isdigit():
        a = int(num)
        if a > 0:
            try:
                finish_data = data[chat_id][a - 1]
                bot.send_message(chat_id, f'Ваша заметка под номером {num}:\n"{finish_data}"')
            except IndexError:
                bot.send_message(chat_id, f'Заметки под таким номером не существует, попробуйте еще раз')
                find_notes = bot.send_message(chat_id, f'Введите номер или слово из заметки, которую желаете найти')
                bot.register_next_step_handler(find_notes, find_note)
    elif num.isdigit() != int:
        user_data = data[chat_id]
        founded_data = []
        for index, el in enumerate(user_data):
            if num.lower() in el.lower():
                founded_data.append(f'{index + 1}. {el} \n')
            else:
                bot.send_message(chat_id, f'Нет заметки с таким словом, попробуйте еще раз')
                find_notes = bot.send_message(chat_id, f'Введите номер или слово из заметки, которую желаете найти')
                bot.register_next_step_handler(find_notes, find_note)
        bot.send_message(chat_id, ''.join(founded_data))
    else:
        bot.send_message(chat_id, f'Неверный номер, попробуйте еще раз')
        find_notes = bot.send_message(chat_id, f'Введите номер или слово из заметки, которую желаете найти')
        bot.register_next_step_handler(find_notes, find_note)


def delete_note(message):
    chat_id = message.chat.id
    num = message.text
    if num.isdigit():
        user_data = data[chat_id]
        a = int(num)
        if a > 0:
            try:
                deleted_data = user_data.pop(a - 1)
                bot.send_message(chat_id, f'Заметка "{deleted_data}" успешно была удалена!')
            except IndexError:
                bot.send_message(chat_id, f'Заметка с таким номером не существует, попробуйте еще раз')
                delete_notes = bot.send_message(chat_id, f'Введите номер заметки, которую желаете удалить')
                bot.register_next_step_handler(delete_notes, delete_note)
    else:
        bot.send_message(chat_id, f'Неверный номер, попробуйте еще раз')
        delete_notes = bot.send_message(chat_id, f'Введите номер заметки, которую желаете удалить')
        bot.register_next_step_handler(delete_notes, delete_note)
    bot.send_message(chat_id, f'Не забудьте нажать на кнопку "Сохранить изменения", чтобы сохранить изменения')


def saved_data(message):
    chat_id = message.chat.id
    with open('saved_dictionary.pkl', 'wb') as saved:
        pickle.dump(data, saved)
    bot.send_message(chat_id, 'Изменения успешно сохранены!')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
