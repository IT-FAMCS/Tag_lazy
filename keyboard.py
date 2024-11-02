from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

def one_keyboard():
    keyboard = ReplyKeyboardMarkup( [[KeyboardButton("/create_poll")]], resize_keyboard=True, one_time_keyboard=True)
    return keyboard