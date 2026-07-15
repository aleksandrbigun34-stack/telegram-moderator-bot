import telebot
from telebot import types
import random
import json
import os
import threading
import http.server
import socketserver
def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()
        threading.Thread(target=run_web_server, daemon=True).start()
bot=telebot.TeleBot(os.environ.get("BOT_TOKEN"))
bad_words=["чит","спам","купи","задонать","подари","дай","67"]
DB_FILE="warnings_db.json"
def load_warnings():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return{int(k):v for k, v in json.load(f).items()}
        except:
            return{}
    return{}
def save_warnings():
        with open(DB_FILE, "w") as f:
            json.dump(warnings, f)
warnings=load_warnings()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup=types.InlineKeyboardMarkup(row_width=2)
    btn_yt=types.InlineKeyboardButton("Мой YouTube-канал 🎬", url="https://youtube.com")
    btn_rules=types.InlineKeyboardButton("Правила чата", callback_data="show_rules")
    markup.add(btn_yt, btn_rules)
    bot.send_message(message, f"Здорово, {message.from_user.first_name}! 👋\nЯ твой личный модератор.Вибирай действие на кнопках снизу:", reply_markup=markup)
@bot.message_handler(commands=['dice'])
def roll_dice(message):
    bot.send_dice(message.chat.id)
@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        warnings[user_id] = 0
        save_warnings()
        bot.send_message(message.chat.id, f"Амнистия! Предупреждения для @{message.reply_to_message.from_user.username} сброшены! 👍")
    else:
        bot.send_message(message.chat.id, "Ответь командой /unwarn на сообщение того, кого хочешь помиловать.")
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "show_rules":
        bot.send_message(call.message.chat.id, "📜 Правила чата:\n1. Никаких читов! ❌\n2. Не спамить и не просить подарки! 🚫\n3. Быть вежливым.")
        bot.answer_callback_query(call.id)
@bot.message_handler(func=lambda message: True)
def filter_messages(message):
    text = message.text.lower()
    for word in bad_words:
        if word in text:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение:{є}")
            user_id = message.from_user.id
            warnings[user_id] = warnings.get(user_id, 0) + 1
            save_warnings()
            if warnings[user_id] >= 3:
                bot.send_message(message.chat.id, f"Користувач {message.from_user.first_name} порушив правила 3 раза і відлітає в бан!")
                try:
                    bot.ban_chat_member(message.chat.id, user_id)
                except:
                    bot.send_message(message.chat.id, "Я хотел тебя забанить, но у меня нет прав админа! 😅")
            else:
                bot.send_message(message.chat.id, f"Попередження для {message.from_user.first_name}! У вас вже {warnings[user_id]}/3 варнів. Поводьтеся ввічливо!")
            break
bot.polling(none_stop=True)

