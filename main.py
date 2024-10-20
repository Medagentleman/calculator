import telebot
from telebot import types
import re
import math
import logging

# Настройка логирования. Логи будут выводиться в формате времени, уровня и сообщения.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Создаем экземпляр бота с токеном
bot = telebot.TeleBot('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

# Словарь для хранения текущих математических выражений пользователей по их chat_id
user_data = {}

# Разрешены только цифры, математические операторы и определенные функции
# Регулярное выражение для проверки допустимых символов в выражении
allowed_chars = re.compile(r'^[\d+\-*/.()%sqrt^ ]+$')


# Функция для проверки допустимости выражения
# Она возвращает True, если выражение соответствует регулярному выражению allowed_chars
def is_valid_expression(expression):
    return bool(allowed_chars.match(expression))


# Безопасное выполнение математического выражения
def safe_eval(expression, user_info):
    if is_valid_expression(expression):
        try:
            # Замена символов для выполнения дополнительных функций
            expression = expression.replace('^', '**')  # Замена символа '^' на '**' для возведения в степень
            expression = expression.replace('sqrt',
                                            'math.sqrt')  # Замена 'sqrt' на функцию math.sqrt для вычисления корня

            # Логируем выражение перед выполнением для отслеживания
            logging.info(f"User {user_info} evaluating expression: {expression}")

            # Выполнение выражения с использованием eval, безопасно ограничив доступ только к математическим функциям
            result = str(eval(expression, {"__builtins__": None, "math": math}, {}))

            # Логируем результат вычисления
            logging.info(f"User {user_info} result: {result}")
            return result
        except Exception as e:
            # Логируем любые ошибки, которые могут возникнуть во время вычислений
            logging.error(f"User {user_info} error evaluating expression: {expression}, Error: {e}")
            return "Ошибка"  # Возвращаем сообщение об ошибке пользователю
    else:
        # Логируем случаи, когда выражение не является допустимым
        logging.warning(f"User {user_info} invalid expression: {expression}")
        return "Недопустимое выражение"


# Функция для создания клавиатуры, имитирующей кнопки калькулятора
def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()  # Создаем объект клавиатуры

    # Определяем кнопки, которые будут отображаться на клавиатуре
    buttons = [
        ['7', '8', '9', '/'],  # Верхний ряд с цифрами и делением
        ['4', '5', '6', '*'],  # Средний ряд с цифрами и умножением
        ['1', '2', '3', '-'],  # Нижний ряд с цифрами и вычитанием
        ['0', '.', '=', '+'],  # Ряд с нулем, точкой, равно и сложением
        ['C', '(', ')', '%'],  # Ряд с кнопкой очистки, скобками и процентами
        ['sqrt', '^', 'sin', 'cos', 'tan']  # Ряд с квадратным корнем, степенью и тригонометрическими функциями
    ]

    # Преобразуем каждый ряд кнопок в объект кнопки и добавляем на клавиатуру
    for row in buttons:
        row_buttons = [types.InlineKeyboardButton(text=btn, callback_data=btn) for btn in row]
        keyboard.row(*row_buttons)

    return keyboard  # Возвращаем созданную клавиатуру


# Функция для получения информации о пользователе для логирования
def get_user_info(user):
    username = user.username or "No username"  # Если у пользователя нет никнейма, используем текст "No username"
    first_name = user.first_name or "No first name"  # Если у пользователя нет имени, используем текст "No first name"
    user_id = user.id  # ID пользователя
    return f"ID: {user_id}, Name: {first_name}, Username: @{username}"


# Обрабатываем команду "/start", отправляем приветственное сообщение и создаем клавиатуру
@bot.message_handler(commands=['start'])
def start(message):
    user_info = get_user_info(message.from_user)  # Получаем данные о пользователе
    logging.info(f"User {user_info} started the bot.")  # Логируем событие старта
    # Отправляем сообщение с приветствием и клавиатурой калькулятора
    bot.send_message(message.chat.id, "Добро пожаловать в улучшенный калькулятор!", reply_markup=create_keyboard())
    user_data[message.chat.id] = ""  # Инициализируем пустое выражение для пользователя


# Обрабатываем нажатия на кнопки калькулятора
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id  # Получаем ID чата
    user_info = get_user_info(call.from_user)  # Получаем информацию о пользователе
    current_expression = user_data.get(chat_id, "")  # Получаем текущее выражение пользователя

    # Обрабатываем нажатие кнопки "C" для очистки выражения
    if call.data == "C":
        logging.info(f"User {user_info} cleared the expression.")  # Логируем очистку выражения
        user_data[chat_id] = ""  # Очищаем выражение
        bot.edit_message_text("0", chat_id, call.message.id,
                              reply_markup=create_keyboard())  # Обновляем текст сообщения на "0"

    # Обрабатываем нажатие кнопки "=" для вычисления выражения
    elif call.data == "=":
        result = safe_eval(current_expression, user_info)  # Вызываем функцию безопасного вычисления
        bot.edit_message_text(result, chat_id, call.message.id,
                              reply_markup=create_keyboard())  # Отправляем результат вычисления
        user_data[chat_id] = ""  # Очищаем выражение после вычисления

    # Обрабатываем нажатия других кнопок (цифры и операторы)
    else:
        user_data[chat_id] = current_expression + call.data  # Добавляем нажатую кнопку к текущему выражению
        logging.info(f"User {user_info} updated expression: {user_data[chat_id]}")  # Логируем обновленное выражение
        bot.edit_message_text(user_data[chat_id], chat_id, call.message.id,
                              reply_markup=create_keyboard())  # Обновляем текст сообщения


# Запуск бота с постоянной проверкой входящих сообщений
logging.info("Bot started. Waiting for messages...")  # Логируем старт бота
bot.polling()  # Запускаем опрос API Telegram для получения новых сообщений
