import telebot
from bot_token import bot_token
from util import *
import logging

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

try:
    bot = telebot.TeleBot(bot_token)
except Exception as ex:
    logger.error("Bot init error : " + str(ex))
    exit(-1)
else:
    logger.info("Bot init successful")


@bot.message_handler(commands=['start', 'help', 'помощь'])
def send_welcome(message):
    logger.info("Received help command request " + str(message))
    help_msg = "Бот - валютный ассистент\n\nПоддерживаемый функционал:\nВывод курса цб на текщую дату\n" + \
               "Вывод курса цб на любую дату в формате <b>ДД.ММ.ГГГГ</b>\nВывод информации о курсах банков: \n" + \
               str(banks_rus) + "\nДанные отделений конкретных регионов - 18 крупнейших городов <i>(по умолчанию Москва)</i>\n" + \
               "Поддерживаемые валюты: Доллар США, Евро, Фунт стерлингов, Иена, Юань\n" + \
               "<i>Запросы на английском языке работают в тестовом режиме, рекомендовано использовать русский</i>"
    try:
        bot.send_message(message.chat.id, help_msg, parse_mode="HTML")
    except Exception as ex:
        logger.error("Failed ro reply to message : " + str(ex))
    else:
        logger.info("Reply to help command has been sent successfully")


# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.send_message(message.chat.id, message.text)

@bot.message_handler(func=lambda message: True)
def super_function(message):
    logger.info("Received new message : " + str(message))
    text = str(message.text.lower())
    reply = construct_reply(text)
    try:
        bot.send_message(message.chat.id, reply, parse_mode="HTML")
    except Exception as ex:
        logger.error("Failed ro reply to message : " + str(ex))
    else:
        logger.info("Reply to previous request has been sent successfully.")


for i in range(5):
    try:
        bot.polling()
    except Exception as ex:
        logger.error("Unexpected error : " + str(ex) + "\t trying to reconnect...")
logger.critical("Bot execution has stopped")
