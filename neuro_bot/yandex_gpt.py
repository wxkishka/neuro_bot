# Модуль работы с нейросетью Яндекса.
import requests
import logging  # модуль для сбора логов
# импортирую константы из config файла
from config import (LOGS, MAX_GPT_TOKENS, SYSTEM_PROMPT)  #, IAMTOKEN, FOLDER_ID)
# импортирую модуль для получения токенов
from creds import get_creds
# получаю iam_token и folder_id
iam_token, folder_id = get_creds()

# настраиваю запись событий в лог файл.
logging.basicConfig(filename=LOGS, level=logging.ERROR, format='%(asctime)s'
                    'FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s', filemode='w')


# Определяю количество токенов в сообщении.
def count_gpt_tokens(messages):
    """Функция возрвращает количество токенов в сообщении."""
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion'
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f'gpt://{folder_id}/yandexgpt-lite',
        "messages": messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0


def ask_gpt(messages):
    """Функция отправляет запрос и возвращает ответ от GPT."""
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f'gpt://{folder_id}/yandexgpt-lite',
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": MAX_GPT_TOKENS
        },
        "messages": SYSTEM_PROMPT + messages  # добавляем к системному сообщению предыдущие сообщения
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        # Проверяю ответ на ошибки
        if response.status_code != 200:
            return False, f"Ошибка GPT. Статус-код: {response.status_code}", None
        # Если ошибок нет, возвращаю статус, ответ GPT, и подсчитываю количество токенов в ответе.
        answer = response.json()['result']['alternatives'][0]['message']['text']
        tokens_in_answer = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
        return True, answer, tokens_in_answer
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return False, "Ошибка при обращении к GPT",  None
