import math
import logging  # модуль для сбора логов
import math  # математический модуль для округления
# подтягиваем константы из config файла
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS, TG_TOKEN
# подтягиваем функции для работы с БД
from database import count_users, count_all_limits, count_all_blocks, count_all_symbol
# подтягиваем функцию для подсчета токенов в списке сообщений
from yandex_gpt import count_gpt_tokens
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

bot = TeleBot(TG_TOKEN)
error_message = False

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""

# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    error_message = ''
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        error_message = f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
        return None, error_message
    return all_tokens, error_message

# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):
    error_message = ''
    # user_id = message.from_user.id
    print("stt user_id =", user_id)
    # Переводим секунды в аудиоблоки
    audio_blocks = math.ceil(duration / 15) # округляем в большую сторону
    print("stt_audio_blocks =", audio_blocks)
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = count_all_blocks(user_id) + audio_blocks
    print("stt_all_blocks =", all_blocks)
    all_blocks_count = count_all_limits(user_id, 'stt_blocks')+ audio_blocks
    print("stt_all_blocks_count =", all_blocks_count)
    # Проверяем, что аудио длится меньше 30 секунд
    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        bot.send_message(user_id, msg)
        error_message = msg
        return None, error_message

    # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        # bot.send_message(user_id, msg)
        error_message = msg
        return None, error_message

    return audio_blocks, error_message

# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    error_message =''
    # user_id = message.from_user.id
    print(f"tts_user_id, text = ", user_id, text)
    text_symbols = len(text)
    print(f"tts_text_symbols = ", text_symbols)
    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_symbol(user_id) + text_symbols
    print(f"tts_all_symbols = ", all_symbols)
    all_symbols_count = count_all_limits(user_id, 'tts_symbols') + text_symbols
    print(f"tts_all_symbols_count = ", all_symbols_count)

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        # bot.send_message(user_id, msg)
        error_message = msg
        return None, error_message

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        # bot.send_message(user_id, msg)
        error_message = msg
        return None, error_message
    print(f'tts_text = ', text)
    return len(text), error_message

