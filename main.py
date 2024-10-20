import telebot
from telebot import types
import re
import math
import logging

# Logging configuration. Logs will be output in the format of time, level, and message.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a bot instance with the token
bot = telebot.TeleBot('YOUR_TOKEN_HERE')

# Dictionary to store current mathematical expressions for users by their chat_id
user_data = {}

# Only digits, mathematical operators, and certain functions are allowed
# Regular expression to check for valid characters in the expression
allowed_chars = re.compile(r'^[\d+\-*/.()%sqrt^ ]+$')

# Function to check if the expression is valid
# It returns True if the expression matches the regular expression allowed_chars
def is_valid_expression(expression):
    return bool(allowed_chars.match(expression))

# Safe evaluation of mathematical expression
def safe_eval(expression, user_info):
    if is_valid_expression(expression):
        try:
            # Replace symbols for additional functions
            expression = expression.replace('^', '**')  # Replace '^' with '**' for exponentiation
            expression = expression.replace('sqrt', 'math.sqrt')  # Replace 'sqrt' with math.sqrt for square root

            # Log the expression before evaluating to track user actions
            logging.info(f"User {user_info} evaluating expression: {expression}")

            # Evaluate the expression using eval, limiting access only to math functions for safety
            result = str(eval(expression, {"__builtins__": None, "math": math}, {}))

            # Log the result of the evaluation
            logging.info(f"User {user_info} result: {result}")
            return result
        except Exception as e:
            # Log any errors that occur during evaluation
            logging.error(f"User {user_info} error evaluating expression: {expression}, Error: {e}")
            return "Error"  # Return an error message to the user
    else:
        # Log invalid expressions
        logging.warning(f"User {user_info} invalid expression: {expression}")
        return "Invalid expression"

# Function to create a keyboard simulating calculator buttons
def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()  # Create a keyboard object

    # Define buttons to display on the keyboard
    buttons = [
        ['7', '8', '9', '/'],  # Top row with numbers and division
        ['4', '5', '6', '*'],  # Middle row with numbers and multiplication
        ['1', '2', '3', '-'],  # Bottom row with numbers and subtraction
        ['0', '.', '=', '+'],  # Row with zero, decimal point, equals, and addition
        ['C', '(', ')', '%'],  # Row with clear button, parentheses, and percentage
        ['sqrt', '^', 'sin', 'cos', 'tan']  # Row with square root, exponentiation, and trigonometric functions
    ]

    # Convert each row of buttons into an actual button object and add it to the keyboard
    for row in buttons:
        row_buttons = [types.InlineKeyboardButton(text=btn, callback_data=btn) for btn in row]
        keyboard.row(*row_buttons)

    return keyboard  # Return the created keyboard

# Function to retrieve user information for logging
def get_user_info(user):
    username = user.username or "No username"  # Use "No username" if the user has no username
    first_name = user.first_name or "No first name"  # Use "No first name" if the user has no first name
    user_id = user.id  # Get the user ID
    return f"ID: {user_id}, Name: {first_name}, Username: @{username}"

# Handle the "/start" command, send a welcome message, and create the calculator keyboard
@bot.message_handler(commands=['start'])
def start(message):
    user_info = get_user_info(message.from_user)  # Get the user's info
    logging.info(f"User {user_info} started the bot.")  # Log the start event
    # Send a welcome message with the calculator keyboard
    bot.send_message(message.chat.id, "Welcome to the enhanced calculator!", reply_markup=create_keyboard())
    user_data[message.chat.id] = ""  # Initialize an empty expression for the user

# Handle button presses on the calculator
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id  # Get the chat ID
    user_info = get_user_info(call.from_user)  # Get the user's information
    current_expression = user_data.get(chat_id, "")  # Get the current expression of the user

    # Handle the "C" button press to clear the expression
    if call.data == "C":
        logging.info(f"User {user_info} cleared the expression.")  # Log the expression clear event
        user_data[chat_id] = ""  # Clear the expression
        bot.edit_message_text("0", chat_id, call.message.id, reply_markup=create_keyboard())  # Update the message text to "0"
    
    # Handle the "=" button press to evaluate the expression
    elif call.data == "=":
        result = safe_eval(current_expression, user_info)  # Call the safe evaluation function
        bot.edit_message_text(result, chat_id, call.message.id, reply_markup=create_keyboard())  # Send the result of the evaluation
        user_data[chat_id] = ""  # Clear the expression after the calculation
    
    # Handle other button presses (numbers and operators)
    else:
        user_data[chat_id] = current_expression + call.data  # Append the pressed button to the current expression
        logging.info(f"User {user_info} updated expression: {user_data[chat_id]}")  # Log the updated expression
        bot.edit_message_text(user_data[chat_id], chat_id, call.message.id, reply_markup=create_keyboard())  # Update the message text

# Start the bot and keep polling for new messages
logging.info("Bot started. Waiting for messages...")  # Log the bot start
bot.polling()  # Start polling the Telegram API for new messages
