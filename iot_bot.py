from tapo import Tapo
import telebot
import requests
import logging
from configparser import ConfigParser

logger = telebot.logger
telebot.logger.setLevel(logging.WARNING)

config = ConfigParser()
config.read('tapo_lib/tapo.ini')
IP_TAPO_DEVICE = config["Credentials"]["ip"]
config.read('bot.ini')
KEY = config["Bot"]["key"]
ID_ADMIN = int(config["Bot"]["id_admin"])


# region filters
def IsAdmin(message):
    return message.chat.id==ID_ADMIN

#endregion filters

bot = telebot.TeleBot(KEY, parse_mode=None)

@bot.message_handler(commands=["start",])
def welcome(message):
    bot.reply_to(message,"Hello world")

@bot.message_handler(commands=["on",], func=IsAdmin)
def turnOnTapo(message):
    tapo = Tapo(IP_TAPO_DEVICE)
    tapo.turnOn()
    name = tapo.getDeviceName()
    if (tapo.isOn()):
        bot.reply_to(message, f"{name} is On")
    else:
        bot.reply_to(message, "Error")

@bot.message_handler(commands=["off",], func=IsAdmin)
def turnOffTapo(message):
    tapo = Tapo(IP_TAPO_DEVICE)
    tapo.turnOff()
    name = tapo.getDeviceName()
    if (not tapo.isOn()):
        bot.reply_to(message, f"{name} is Off")
    else:
        bot.reply_to(message, "Error")

@bot.message_handler(commands=["on", "off",])
def turnOnPlugNotAllowed(message):
    bot.reply_to(message, "Permission Denied")

@bot.message_handler(content_types=["voice",])
def parse_audio_message(message):
    file_id = message.voice.file_id
    file = None
    try:
        file_info = bot.get_file(file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(KEY, file_info.file_path))
    except:
        pass
    if file is None: 
        bot.reply_to(message, "Not implemented yet, whisper coming")
    else:
        #binary
        bot.send_audio(message.chat.id, file._content)
        bot.send_audio(message.chat.id, "FILEID")

@bot.message_handler(func=IsAdmin)
def AdminMessage(message):
    bot.reply_to(message, message.text+" Admin")

@bot.message_handler(func= lambda message: True)
def all_resp(message):
    #debug
    print(message.from_user.username)
    print(message.from_user.id)
    bot.reply_to(message, message.text)

bot.infinity_polling()