import telebot
from telebot import types

token = '8015756822:AAGk1uyMJlvOkGSFJ7NUyMlfSO2SlWgOCKA'
bot = telebot.TeleBot(token)

# Словарь для отслеживания состояния пользователей
user_states = {}
# Словарь для хранения введенных пользователями параметров
user_params = {}

# Состояния
ASKING_FIRST_PARAM = "first_param"
ASKING_SECOND_PARAM = "second_param"
ASKING_THIRD_PARAM = "third_param"
RESULT = 'result'


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Ввести параметры')
    markup.add(btn)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}! Я помогу определить цену аренды. Нажмите "Ввести '
                     f'параметры" для начала.',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def parameter_input(message):
    user_id = message.from_user.username

    if message.text == 'Ввести параметры':
        # Устанавливаем состояние для ввода первого параметра и инициализируем параметры
        user_states[user_id] = ASKING_FIRST_PARAM
        user_params[user_id] = {}  # Инициализируем пустой словарь для хранения параметров
        print(user_params, user_states)
        ask_first_param(message)

    elif message.text == 'В главное меню':
        # Сбрасываем состояние и параметры
        user_states.pop(user_id, None)
        user_params.pop(user_id, None)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('Ввести параметры')
        markup.add(btn)
        bot.send_message(message.chat.id, 'Укажите, что вы хотите сделать:', reply_markup=markup)

    elif message.text == 'Назад' or message.text == 'Да' or message.text == 'Нет':
        if user_states.get(user_id) == ASKING_SECOND_PARAM:
            user_states[user_id] = ASKING_FIRST_PARAM
            ask_first_param(message)
        elif user_states.get(user_id) == ASKING_THIRD_PARAM:
            user_states[user_id] = ASKING_SECOND_PARAM
            ask_second_param(message)
        elif user_states.get(user_id) == RESULT and message.text == 'Нет':
            user_states[user_id] = ASKING_THIRD_PARAM
            ask_third_param(message)
        elif message.text == 'Да':
            user_states.pop(user_id)
            user_params.pop(user_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('В главное меню'))
            bot.send_message(message.chat.id, 'Аренда квартиры будет стоить n руб/м', reply_markup=markup)

    else:
        current_state = user_states.get(user_id)
        try:
            param = int(message.text)
            # Сохраняем параметр в словаре user_params
            if current_state == ASKING_FIRST_PARAM:
                user_params[user_id]['1'] = param
                user_states[user_id] = ASKING_SECOND_PARAM
                ask_second_param(message)
            elif current_state == ASKING_SECOND_PARAM:
                user_params[user_id]['2'] = param
                user_states[user_id] = ASKING_THIRD_PARAM
                ask_third_param(message)
            elif current_state == ASKING_THIRD_PARAM:
                user_params[user_id]['3'] = param
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton('Нет'))
                markup.add(types.KeyboardButton('Да'))
                bot.send_message(message.chat.id,
                                 f"Введенные параметры:\nПараметр 1: {user_params[user_id]['1']}\nПараметр 2: "
                                 f"{user_params[user_id]['2']}\nПараметр 3: {user_params[user_id]['3']}")
                bot.send_message(message.chat.id, 'Всё верно?', reply_markup=markup)
                user_states[user_id] = RESULT
                print(user_params, user_states)

        except ValueError:
            bot.send_message(message.chat.id, 'Ошибка: введите число.')


def ask_first_param(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('В главное меню'))
    bot.send_message(message.chat.id, 'Введите первый параметр (число):', reply_markup=markup)


def ask_second_param(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Назад'))
    markup.add(types.KeyboardButton('В главное меню'))
    bot.send_message(message.chat.id, 'Введите второй параметр (число):', reply_markup=markup)


def ask_third_param(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Назад'))
    markup.add(types.KeyboardButton('В главное меню'))
    bot.send_message(message.chat.id, 'Введите третий параметр (число):', reply_markup=markup)


# Запуск бота
bot.polling()
