# Модуль с функциями проверок ограничений.

import logging  # модуль для сбора логов
import math
# импортирую константы из файла config.
from config import (LOGS, MAX_USERS, MAX_USER_GPT_TOKENS
                    , MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_CUR_TTS_SYMBOLS)
# подтягиваем функции для работы с БД
from database import count_users, count_all_limits
# подтягиваем функцию для подсчета токенов в списке сообщений
from yandex_gpt import count_gpt_tokens

# настраиваю параметры логирования событий.
logging.basicConfig(filename=LOGS, level=logging.ERROR, format='%(asctime)s' 
                    'FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s', filemode='w')


def is_users_limit(user_id):
    """Функция проверяет ограничение на число 
       уникальных пользователей, кроме самого пользователя."""
    count = count_users(user_id)
    if count is None:
        return False, 'Ошибка при работе с БД'
    if count < MAX_USERS:
        return True, ''
    return False, 'Превышено максимальное количество пользователей!'


def is_gpt_token_limit(messages, total_spent_tokens):
    """Функция проверяет ограничение пользователя по числу токенов GPT."""
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f'Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}'
    return all_tokens, ""


def is_stt_block_limit(user_id, duration):
    """Функция проверяет ограничение пользователя по числу аудиоблоков."""

    audio_blocks = math.ceil(duration / 15) # перевожу секунды в sst блоки
    all_blocks = count_all_limits(user_id, limit_type='stt_blocks') + audio_blocks # всего блоков пользователя

    # Проверка ограничения длительности сообщения
    if duration >= 30:
        error = 'Сообщение должно быть меньше 30 секунд!'
        return None, error

    # Проверяю на максимальное число потраченных блоков
    if all_blocks >= MAX_USER_STT_BLOCKS:
        error = f'Вы превысили максимальный лимит длительности сообщений {MAX_USER_STT_BLOCKS}.'
        f'Вы использовали {all_blocks} блоков, а доступно: {MAX_USER_STT_BLOCKS - all_blocks}.'
        return None, error

    return audio_blocks, ''

# проверяю превышение лимитов пользователя на преобразование текста в аудио.
def is_tts_symbol_limit(user_id, text):
    """Функция проверяет ограничение пользователя на число символов,
       и возвращает длину сообщения в симовлах."""
    print(text)
    text_length = len(text)
    total_symbols = count_all_limits(user_id, limit_type='tts_symbols') + text_length
    
    # Проверяю превышение общего количества символов в сообщениях пользователя.
    if total_symbols >= MAX_USER_TTS_SYMBOLS:
        error = (f'Превышен общий лимит SpeechKit {MAX_USER_TTS_SYMBOLS}.'
              'Использовано: {total_symbols} символов.'
              f'Доступно: {MAX_USER_TTS_SYMBOLS - total_symbols}')
        return None, error

    # Проверяю превышение количества символов в текущем сообщении пользователя.
    if text_length >= MAX_CUR_TTS_SYMBOLS:
        error = (f'Превышен лимит сообщения в {MAX_CUR_TTS_SYMBOLS} символов \n'
                 f'в Вашем сообщении {text_length} символов.')
        return None, error
    
    return text_length, None
