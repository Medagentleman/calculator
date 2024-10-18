import telebot
from telebot import types
import re
import math  # Добавляем для работы с математическими функциями

# Создаем экземпляр бота
bot = telebot.TeleBot('BOT_TOKEN')

# Храним текущие математические выражения
user_data = {}

# Разрешены только цифры, математические операторы и новые функции
allowed_chars = re.compile(r'^[\d+\-*/.()%sqrt^ ]+$')


# Функция для проверки допустимости выражения
def is_valid_expression(expression):
    return bool(allowed_chars.match(expression))


# Безопасное выполнение выражения
def safe_eval(expression):
    if is_valid_expression(expression):
        try:
            # Замена символов для дополнительных функций
            expression = expression.replace('^', '**')  # Возведение в степень
            expression = expression.replace('sqrt', 'math.sqrt')  # Квадратный корень

            return str(eval(expression, {"__builtins__": None, "math": math}, {}))
        except Exception:
            return "Ошибка"
    else:
        return "Недопустимое выражение"


# Создаем клавиатуру с кнопками как у калькулятора
def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    # Создаем кнопки
    buttons = [
        ['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['0', '.', '=', '+'],
        ['C', '(', ')', '%'],  # Добавлена кнопка для процентов и скобки
        ['sqrt', '^', 'sin', 'cos', 'tan']  # Добавлены новые функции
    ]

    for row in buttons:
        row_buttons = [types.InlineKeyboardButton(text=btn, callback_data=btn) for btn in row]
        keyboard.row(*row_buttons)

    return keyboard


# Обрабатываем команды "/start"
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в улучшенный калькулятор!", reply_markup=create_keyboard())
    user_data[message.chat.id] = ""


# Обрабатываем нажатия на кнопки клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    current_expression = user_data.get(chat_id, "")

    if call.data == "C":
        user_data[chat_id] = ""
        bot.edit_message_text("0", chat_id, call.message.id, reply_markup=create_keyboard())
    elif call.data == "=":
        result = safe_eval(current_expression)  # Используем безопасную функцию для вычислений
        bot.edit_message_text(result, chat_id, call.message.id, reply_markup=create_keyboard())
        user_data[chat_id] = ""
    else:
        user_data[chat_id] = current_expression + call.data
        bot.edit_message_text(user_data[chat_id], chat_id, call.message.id, reply_markup=create_keyboard())


# Запуск бота
bot.polling()
