import logging
import os
import requests
import telebot
import time
from telebot import types
from dotenv import load_dotenv


load_dotenv()
secret_token = os.getenv('TOKEN')
RETRY_PERIOD = 60

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='main.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(token=secret_token)
URL = 'https://yesno.wtf/api'


def get_new_response():
    """GET-запрос к эндпоинту. Извлечение картинки и ответа."""
    try:
        response = requests.get(URL).json()
        random_resp = list(map(response.get, ['image', 'answer']))
        random_gif = random_resp[0]
        random_answer = random_resp[1]
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        random_gif = 'https://http.cat/404'
        random_answer = "Что-то пошло не так. Дайте Вселенной время."
    return [random_gif, random_answer]


@bot.message_handler(content_types=['text'])
def start(message):
    """Запуск работы командой start."""
    logger.info('Начало отправки сообщения.')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('/start')
    markup.add(button)
    if message.text == '/start':
        bot.send_message(
            message.from_user.id,
            "Магический бот приветствует тебя. Сосредоточься. "
            "И задай мне свой вопрос...",
            reply_markup=markup)
        bot.register_next_step_handler(message, get_question)
    else:
        bot.send_message(
            message.from_user.id,
            'Чтобы начать, напиши /start',
            reply_markup=markup)
        logger.info('Не запущена команда /start.')


def get_question(message):
    """Фильтрация вопросов и получение ответа."""
    words = ['Как', 'Почему', 'Где', 'Зачем', 'Кто', 'Что', 'Когда', 'Сколько']
    result = 0
    for word in words:
        if isinstance(message.text, str) is True and word in message.text:
            result = 1
    if isinstance(message.text, str) is False:
        bot.send_message(message.from_user.id, "Задайте вопрос текстом.")
        logger.info('Формат вопроса - не текст.')
        bot.register_next_step_handler(message, get_question)
    elif result == 1:
        bot.send_message(
            message.from_user.id,
            "Неверный формат вопроса."
            " Задай вопрос, на который можно ответить 'да' или 'нет'.")
        logger.info('На вопрос нельзя ответить да или нет.')
        bot.register_next_step_handler(message, get_question)
    elif '?' not in message.text:
        bot.send_message(message.from_user.id, "Это не вопрос.")
        logger.info('Формат сообщения - не вопрос.')
        bot.register_next_step_handler(message, get_question)
    else:
        if get_new_response()[0] == 'https://http.cat/404':
            bot.send_photo(message.from_user.id, get_new_response()[0])
        else:
            bot.send_video(message.from_user.id, get_new_response()[0])
        bot.send_message(message.from_user.id, text=get_new_response()[1])


def main():
    """Основная логика работы бота."""
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(e)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
