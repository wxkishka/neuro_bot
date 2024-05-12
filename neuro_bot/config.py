# Модуль настроек Нейро-бота

TOKEN = '6787855008:AAFNpFZ-Y1DD_x1mV0UYoPqH0AVwTW9iacQ'  # token телеграм-бота
IAMTOKEN = 't1.9euelZrIlZPOzoqcyInJyo2LzcaWy-3rnpWajM2emZvPmYqJlsaSlpmQnI3l8_cLB35N-e93IHEM_t3z90s1e03573cgcQz-zef1656Vmp6Xj86QzJCUmJ6SyY7LkJiN7_zF656Vmp6Xj86QzJCUmJ6SyY7LkJiNveuelZqMzJybjouSzYzOy8yKlJePnrXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.Bh8-HNeYApXsGadB6jze4jYneMGmokMd-3A4QHWGMo02LOlS4h5rG6mKScfF7HMEcPyAoU_aL_upzllHKStXBQ'  # токен для YandexGPT
FOLDER_ID = 'b1gr1l4ru3gbjel7ihgi'  # FoldeID для работы с Yandex GPT

HOME_DIR = '/home/student/neuro_bot/neuro_bot'  # путь к папке с проектом
IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iamtoken.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folderid.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/token.txt'  # файл для хранения bot_token

STT_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
TTS_URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # Максимальное число аудиоблоков.
MAX_USER_TTS_SYMBOLS = 50_000  # Максимальное число символов на пользователя.
MAX_USER_GPT_TOKENS = 2_000  # Максимльное число GPT токенов на пользователя.
MAX_CUR_TTS_SYMBOLS = 500  # Максимальное число символов в сообщении пользователя.

LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_NAME = f'{HOME_DIR}/messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Давай короткие ответы. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом
