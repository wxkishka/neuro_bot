# Модуль для работы с базой данных.
import sqlite3
import logging

from config import LOGS, DB_NAME

# настраиваю запись логов в файл.
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format='%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s', filemode='w')


def create_database(DB_NAME):
    """Функция создания базы данных и таблицы messges."""
    try:
        # подключаюсь к базе данных.
        with sqlite3.connect(DB_NAME) as con:
            cursor = con.cursor()
            # создаю таблицу для хранения данных пользователя.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                role TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            # Если база создана, записываю в лог файл.
            logging.info('DATABASE: База данных создана')
    except Exception as e:
        logging.error(e)  # Записываю ошибку в лог файл.
        return None


def add_message(user_id, full_message):
    """Функция добавляет запись данных пользователя в базу данных"""
    try:
        # подключаюсь к базе данных.
        with sqlite3.connect(DB_NAME) as con:
            cursor = con.cursor()
            message, role, total_gpt_tokens, tts_symbols, stt_blocks = full_message
            # записываю новое сообщение в базу данных.
            sql = '''INSERT INTO messages (user_id, message, role,
                     total_gpt_tokens, tts_symbols, stt_blocks) 
                     VALUES (?, ?, ?, ?, ?, ?)'''
            cursor.execute(sql,
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            con.commit()
            logging.info(f'DATABASE: INSERT INTO messages '
                         f'VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})')
    except Exception as e:
        logging.error(e)
        return None


def count_users(user_id):
    """Функция возращает количество уникальных пользователей."""
    try:
        with sqlite3.connect(DB_NAME) as con:
            cursor = con.cursor()
            sql = '''SELECT COUNT(DISTINCT user_id) 
                     FROM messages WHERE user_id <> ?'''
            cursor.execute(sql, (user_id,))
            count = cursor.fetchone()[0]
            return count 
    except Exception as e:
        logging.error(e)
        return None


def get_last_messages(user_id, last_messages):
    """Функция возвращает заданное количество последних сообщений."""
    messages = []  # список сообщений.
    total_spent_tokens = 0  # общее количество потраченных токенов.
    try:
        with sqlite3.connect(DB_NAME) as con:
            cursor = con.cursor()
            sql = '''SELECT message, role, total_gpt_tokens 
                     FROM messages WHERE user_id=?
                     ORDER BY id DESC LIMIT ?'''
            cursor.execute(sql, (user_id, last_messages,))
            data = cursor.fetchall()
            # проверяю есть ли в data данные, и есть ли в data[0] сообщения.
            if data and data[0]:
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])
            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e)
        return messages, total_spent_tokens


def count_all_limits(user_id, limit_type):
    """Функция подсчитывает количество потраченных симоволов или аудиоблоков."""
    try:
        with sqlite3.connect(DB_NAME) as con:
            cursor = con.cursor()
            # считаем лимиты по <limit_type>, которые использовал пользователь
            cursor.execute(f'''SELECT SUM({limit_type}) 
                           FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            # проверяем data на наличие хоть какого-то полученного результата запроса
            # и на то, что в результате запроса мы получили какое-то число в data[0]
            if data and data[0]:
                # если результат есть и data[0] == какому-то числу, то:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]  # возвращаем это число - сумму всех потраченных <limit_type>
            else:
                # результата нет, так как у нас ещё нет записей о потраченных <limit_type>
                return 0  # возвращаем 0
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0
