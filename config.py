import os

from dotenv import load_dotenv

load_dotenv()

ADMINS_IDS = os.getenv('ADMINS_ID')
TG_TOKEN = os.getenv('TG_TOKEN') # token телеграм-бота
FOLDER_ID = os.getenv('FOLDER_ID')
GPT_TOKEN = os.getenv('GPT_TOKEN')
IAM_TOKEN = os.getenv('GPT_TOKEN')

TOKENIZER_URL = os.getenv('TOKENIZER_URL')
GPT_URL = os.getenv('GPT_URL')

GPT_MODEL = os.getenv('GPT_MODEL')

MAX_TOKENS_IN_SESSION = 500
MAX_TOKENS_FOR_ANSWER = 200
MAX_SESSIONS = 5

TOKEN = os.getenv('TG_TOKEN') # token телеграм-бота
MAX_USERS = 3 # максимальное кол-во пользователей

MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 15  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5  # 5 000 символов
MAX_USER_GPT_TOKENS = 3_500  # 3 000 токенов
MAX_TTS_SYMBOLS = 5

DB_NAME = "messages.db"
LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'
                                            'Отвечай кратко, не более 150 символов'}]  # список с системным промтом



HEADERS = {'Authorization': f'Bearer {GPT_TOKEN}'}
DEFAULT_DATA = {
    "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
    "completionOptions": {
        "stream": False,
        "temperature": 0.7,
        "maxTokens": MAX_TOKENS_FOR_ANSWER
    },
}
