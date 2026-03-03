import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

users = {}
stock = {
    10: [],
    20: [],
    50: []
}

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🛒 Buy Code", callback_data="buy"))
    markup.row(InlineKeyboardButton("🎁 Redeem Points", callback_data="redeem"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in users:
        users[user_id] = {"points": 0}
    bot.send_message(user_id, "Welcome To Google Play Code Bot", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.message.chat.id

    if call.data == "buy":
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("₹10 Code", callback_data="buy_10"))
        markup.row(InlineKeyboardButton("₹20 Code", callback_data="buy_20"))
        markup.row(InlineKeyboardButton("₹50 Code", callback_data="buy_50"))
        bot.edit_message_text("Select Amount:", user_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("buy_"):
        amount = int(call.data.split("_")[1])
        if users[user_id]["points"] < amount:
            bot.answer_callback_query(call.id, "Not enough points")
        elif len(stock[amount]) == 0:
            bot.answer_callback_query(call.id, "Out of stock")
        else:
            code = stock[amount].pop(0)
            users[user_id]["points"] -= amount
            bot.send_message(user_id, f"Your Code: {code}")

    elif call.data == "redeem":
        msg = bot.send_message(user_id, "Send your redeem code:")
        bot.register_next_step_handler(msg, process_redeem)

def process_redeem(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        users[user_id]["points"] += amount
        bot.send_message(user_id, f"{amount} Points Added Successfully")
    except:
        bot.send_message(user_id, "Invalid Code")

@bot.message_handler(commands=['addcode'])
def add_code(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split()
            amount = int(parts[1])
            code = parts[2]
            stock[amount].append(code)
            bot.send_message(message.chat.id, "Code Added Successfully")
        except:
            bot.send_message(message.chat.id, "Format: /addcode 10 ABCD-1234")

bot.infinity_polling()
