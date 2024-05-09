# Модуль настроек Нейро-бота

TOKEN = '5924781016:AAFe6DmVlFmhFGWE18Y-wSfFN6gcHzrh3Zk'  # token телеграм-бота
IAMTOKEN = 't1.9euelZqYjpPMzJiMjsyVmcjKm5rNze3rnpWajM2emZvPmYqJlsaSlpmQnI3l8_d1AyNO-e9NK19J_d3z9zUyIE75700rX0n9zef1656VmpybjZLIiseKyZGWy4qVjpOV7_zF656VmpybjZLIiseKyZGWy4qVjpOVveuelZqQxpCOzMeKx4mTmcqOiZaRybXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.zB3skoyZU4-8rRhHRQlKX_AtTfm30ewpFNoOcGOsQ3pxE3FxKfZ_ONMmuia_2cM5HRHVRTE6aI4pABmpRnaYBQ' # токен для YandexGPT
FOLDER_ID = 'b1gr1l4ru3gbjel7ihgi' # FoldeID для работы с Yandex GPT

STT_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
TTS_URL = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # Максимальное число аудиоблоков.
MAX_USER_TTS_SYMBOLS = 50_000  # Максимальное число символов на пользователя.
MAX_USER_GPT_TOKENS = 2_000  # Максимльное число GPT токенов на пользователя.
MAX_CUR_TTS_SYMBOLS = 500 # Максимальное число символов в сообщении пользователя.

LOGS = 'logs.txt'  # файл для логов
DB_NAME = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Давай короткие ответы. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом
