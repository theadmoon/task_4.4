import telebot
import logging  # модуль для сбора логов
# подтягиваем константы из config-файла
from config import TOKEN, LOGS
from validators import *  # модуль для валидации
from yandex_gpt import ask_gpt  # модуль для работы с GPT
# подтягиваем константы из config файла
from config import TOKEN, LOGS, COUNT_LAST_MSG
# подтягиваем функции из database файла
from database import create_database, add_message, select_n_last_messages, create_table, insert_row
from speechkit import speech_to_text, text_to_speech
from telebot.types import ReplyKeyboardMarkup
from telebot import types
'''
import math
from speechkit import speech_to_text
import logging
import telebot
from telebot import TeleBot
import telebot

from telebot import TeleBot

'''

create_database()
create_table()

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.INFO, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
bot = telebot.TeleBot(TOKEN)  # создаём объект бота

# Функция для создания клавиатуры с нужными кнопками
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
                     text= f"Привет, {user_name}! Отправь мне голосовое сообщение или текст, и я тебе отвечу!\n"
                           f"Выбери кнопку /tts, чтобы проверить синтез речи\n"
                            f" Выбери кнопку /sst, чтобы проверить распознавания речи",
                    reply_markup=create_keyboard(['/tts', "/stt", '/help']))

# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")

# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)
# Обрабатываем команду /stt
@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)


# Переводим голосовое сообщение в текст после команды stt
def stt(message):
    user_id = message.from_user.id

    # Проверка, что сообщение действительно голосовое
    if not message.voice:
        return

    # Считаем аудиоблоки и проверяем сумму потраченных аудиоблоков
    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id  # получаем id голосового сообщения
    print("file_id =", file_id)
    file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
    print("file_info =", file_info)
    file = bot.download_file(file_info.file_path)  # скачиваем голосовое сообщение

    # Получаем статус и содержимое ответа от SpeechKit
    status, text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст
    print("status, text =", status, text)
    # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
    if status:
        # Записываем сообщение и кол-во аудиоблоков в БД
        insert_row(user_id, text, 'stt_blocks', stt_blocks)
        if not text:
            text = "Плохое качество аудио, попробуйте записать звук еще раз"
        bot.send_message(user_id, text, reply_to_message_id=message.id)

        bot.register_next_step_handler(message, stt)
    else:
        bot.send_message(user_id, text)

# Декоратор для обработки голосовых сообщений, полученных ботом
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        user_id = message.from_user.id
        print(f'user_id=', user_id)

        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(user_id)
        print(f'status_check_users, error_message=', status_check_users, error_message)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # Проверка на доступность аудиоблоков
        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        print(f'stt_blocks, error_message=', stt_blocks)
        if error_message:
           bot.send_message(user_id, error_message)
           return

        # Обработка голосового сообщения
        file_id = message.voice.file_id
        print("file_id =", file_id)
        file_info = bot.get_file(file_id)
        print("file_info =", file_info)
        file = bot.download_file(file_info.file_path)

        # Получаем статус и содержимое ответа от SpeechKit
        status_stt, stt_text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст
        print("status, text =", status_stt, stt_text)
        # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
        if status_stt:
            if not stt_text:
                stt_text = "Плохое качество аудио, попробуйте записать звук еще раз"
                bot.send_message(user_id, stt_text, reply_to_message_id=message.id)
                bot.register_next_step_handler(message, handle_voice)
        else:
            bot.send_message(user_id, stt_text)
            return
        '''
        status_stt, stt_text = speech_to_text(file)
        print("status_stt, stt_text =", status_stt, stt_text)
        if not status_stt:
           bot.send_message(user_id, stt_text)
           return
        '''
        # Запись в БД

        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        # Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        print("last_messages, total_spent_tokens = ", last_messages, total_spent_tokens)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        print("total_gpt_tokens, error_message = ", total_gpt_tokens, error_message)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        # Запрос к GPT и обработка ответа
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        print("status_gpt, answer_gpt, tokens_in_answer = ", status_gpt, answer_gpt, tokens_in_answer)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer
        print("total_gpt_tokens = ", total_gpt_tokens)

        # Проверка на лимит символов для SpeechKit
        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)
        if error_message:
           bot.send_message(user_id, error_message)
           return
        print("tts_symbols = is_tts_symbol_limit(user_id, answer_gpt) = ", tts_symbols)

        # Запись ответа GPT в БД

        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        # Преобразование ответа в аудио и отправка
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй записать другое сообщение")


'''
# обрабатываем голосовые сообщения
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    ...


# тут пока что пусто, заходи сюда в следующем уроке =)
'''
# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


...

'''
# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)

        # БД: добавляем сообщение пользователя в базу данных

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
        # если что-то пошло не так, уведомляем пользователя и прекращаем выполнение функции
        bot.send_message(user_id, answer_gpt)
        return

    # БД: добавляем ответ GPT и суммарно потраченные токены в базу данных

    bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю

except Exception as e:
logging.error(e)  # если ошибка - записываем её в логи
bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")
'''

# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")

...

bot.polling()  # запускаем бота