# Основлной модуль Нейро-бота.
import telebot
import logging

# from creds import TOKEN
from config import TOKEN
from config import DB_NAME, LOGS, COUNT_LAST_MSG
from database import create_database, add_message, get_last_messages
from validators import (is_users_limit, is_gpt_token_limit,
                        is_stt_block_limit, is_tts_symbol_limit)
from speechkit import speech_to_text, text_to_speech
from yandex_gpt import ask_gpt

# настраиваю логирование событий.
logging.basicConfig(filename=LOGS, level=logging.ERROR, format='%(asctime)s'
                    'FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s',
                    filemode='w')

# Создаю объект bot.
bot = telebot.TeleBot(TOKEN)

# Создаю базу данных и таблицу для хранения данных пользователя.
create_database(DB_NAME)


@bot.message_handler(commands=['start'])
def start_handler(message):
    """Функция обрабатывает команду /start ."""
    user_name = message.from_user.first_name
    bot.send_message(message.from_user.id, f'Привет {user_name} !'
                                           'Отправь мне голосовое сообщение или текст, и я тебе отвечу!')


@bot.message_handler(commands=['help'])
def help_handler(message):
    """Функция обрабатывает команду help."""
    bot.send_message(message.from_user.id, 'Я Нейробот. Принимаю твои голосовые\n'
                                           'или текстовые сообщения и отвечаю тебе голосом.\n'
                                           'комманда /debug выведет лог файл для отладки/n'
                                           'комманда /stt преобразует аудио сообщение в текстовое \n'
                                           'комманда /tts преобразует текстовое сообщение в аудио.')


@bot.message_handler(commands=['debug'])
def debug(message):
    """Функция обрабатывает команду debug."""
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    """Функция-обработчик команды tts. """
    user_id = message.from_user.id
    bot.send_message(user_id, 'Это сервисный режим для проверки преобразования \n'
                              'текстового сообщения в аудио.')
    bot.register_next_step_handler(message, tts)


def tts(message):
    """Функция проверяет ограничения для пользователей на длину обращений,
       и делает запрос к SpecchKit на создание аудио файла."""
    user_id = message.from_user.id
    text = message.text

    # Получаем статус и содержимое ответа от SpeechKit
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)


@bot.message_handler(commands=['stt'])
def stt_handler(message):
    """Функция обрабатывает комманду stt."""
    user_id = message.from_user.id
    bot.send_message(user_id, 'Это сервисный режим для проверки службы \n'
                              'преобразования аудио сообщения в текствое.')
    bot.register_next_step_handler(message, stt)


def stt(message):
    """Функция переводит голосовое сообщение в текст."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Проверяю сообщение на голосовое
    if not message.voice:
        bot.send_message(chat_id, 'Я принимаю только голосовые!')
        return

    file_id = message.voice.file_id  # получаю id аудио сообщения.
    file_info = bot.get_file(file_id)  # получаю информацию об аудио файле.
    file = bot.download_file(file_info.file_path)  # скачиваю аудои файл.
    # Преобразую аудио сообщение в текствое.
    status, text = speech_to_text(file)

    if status:
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    """Функция преобразует голосовое сообщение в текстовое и обратно,
       отправляет запрос в GPT."""
    try:
        user_id = message.from_user.id  # Идентификатор пользователя.

        # Проверяю максимальное количество пользователей.
        status_check_users, error_message = is_users_limit(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # Проверяю ограничение на аудиоблоки.
        stt_blocks, error = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error)
            return

        # Получаю данные об аудио файле, и загружаю его.
        file_id = message.voice.file_id  # Идентификатор аудио файла.
        file_info = bot.get_file(file_id)  # Информация о файле для загрузки.
        file = bot.download_file(file_info.file_path)  # Загружаю файл по указанному пути.

        # Преобразую голосовое сообщение в текст.
        status_stt, stt_text = speech_to_text(file)  # Получаю текстовое сообщение и статус.
        if not status_stt:
            # Если ошибка, отправляю сообщение об ошибке.
            bot.send_message(user_id, stt_text)
            return

        # Записываю текст сообщения пользователя в базу данных.
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        # Запрашиваю последние сообщения пользователя в количестве COUNT_LAST_MSG
        # в GPT для генерации ответа.
        last_messages, total_spent_tokens = get_last_messages(user_id,
                                                              COUNT_LAST_MSG)
        # Проверяю ограничение на количество токенов.
        total_gpt_tokens, error = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error:
            bot.send_message(user_id, error)
            return
        # Отправляю запрос в GPT.
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            # Если ошибка, отправляю сообщение об ошибке.
            bot.send_message(user_id, answer_gpt)
            return
        # Подсчитываю общее количество потраченных токенов.
        total_gpt_tokens += tokens_in_answer

        # Получаю длину сообщения, проверяю или вывожу ошибку.
        tts_symbols, error = is_tts_symbol_limit(user_id, answer_gpt)

        # Записываю в БД ответ GPT в роль Асситант, потраченные токены
        # и символы на ответ.
        gpt_answer_message = [answer_gpt, 'assistant', total_gpt_tokens,
                              tts_symbols, 0]
        add_message(user_id, gpt_answer_message)

        if error:
            bot.send_message(user_id, error)
            return

        # Преобразую текстовое сообщение в голосовое.
        status_tts, voice_response = text_to_speech(answer_gpt)
        if not status_tts:
            # При ошибке преобразования, отправляю сообщение об ошибке.
            # bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
            bot.send_message(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)

    except Exception as e:
        # Логирование ошибки.
        logging.error(e)
        bot.send_message(message.from_user.id, 'Ошибка в процессе пробразования ответа GPT'
                                               'в голосовое сообщение.')


# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # Проверяю ограничение на количество пользователей.
        user_status, error = is_users_limit(user_id)
        if not user_status:
            bot.send_message(user_id, error)
            return

        # Записываю сообщение пользователя в базу данных.
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id, full_user_message)
        # Проверяю есть ли доступные токены.
        last_messages, total_spent_tokens = get_last_messages(user_id, COUNT_LAST_MSG)
        # считаю общее количество потраченных токенов.
        total_gpt_tokens, error = is_gpt_token_limit(last_messages, total_spent_tokens)

        if error:
            # Если ошибка, отправляю сообщение.
            bot.send_message(user_id, error)
            return

        # Отправляю запрос в GPT.
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # Проверяю ответ GPT на ошибки.
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return

        # Сумма потраченных токенов и токенов ответа GPT.
        total_gpt_tokens += tokens_in_answer

        # Добавляю ответ GPT и сумму потраченных токенов в базу данных.
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id, full_gpt_message)

        # Преобразую текстовое сообщение в аудио.
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)  # Ошибку записываю в лог.
        bot.send_message(message.from_user.id, 'Ошибка при обращении к GPT!')


# обрабатываю все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, 'Отправьте голосовое или текстовое сообщение!')


# Запускаю бота.
bot.infinity_polling()
