# Модуль преобразования голосовых сообщений в текстовые и обратно.
import requests

# from creds import IAMTOKEN, FOLDER_ID
from config import STT_URL, TTS_URL, IAMTOKEN, FOLDER_ID


def speech_to_text(data):
    """Функция отправляет запрос в SpeechKit,
       и преобразует голосовое сообщение в текст."""
    # Заголовок запроса.
    headers = {
        'Authorization': f'Bearer {IAMTOKEN}',
    }
    # Параметры запроса.
    params = '&'.join([
        'topic=general',
        f'folderId={FOLDER_ID}',
        'lang=ru-RU'
    ])
    # Запрос в SpeechKit.    
    response = requests.post(
                f'{STT_URL}?{params}',
                headers=headers,
                data=data)
    
    decoded_data = response.json()
    # Проверяю ответ на ошибки.
    if decoded_data.get('error_code') is None:
        return True, decoded_data.get('result')  # Статус, ответ если нет ошибок.
    else:
        # return False, 'Ошибка при преобразовании речи в текст.'
        return False, decoded_data.get('error_code')
    

def text_to_speech(text):
    """Функция отправляет запрос пользователя в SpeechKit,
        и преобразует текстовое сообщение в речевое."""
    iam_token = IAMTOKEN
    folder_id = FOLDER_ID
    # Заголовок запроса/
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    # Тело запроса/
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': folder_id,
    }
    # Отправляю запрос в SpeechKit.
    response = requests.post(
        # 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        TTS_URL,
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content
    else:
        return False, f'Ошибка при запросе аудио файла: {response.status_code}.' 
