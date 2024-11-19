import pickle
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from rent_bot_token import BOT_TOKEN

# Загрузить модель с диска
loaded_model = pickle.load(open('model_weights.sav', 'rb'))


def result(user_data, user_id):
    # user_vars = [parameter for parameter in user_data[user_id]['parameters'].values()]
    user_vars = []
    for parameter in user_data[user_id]['parameters'].values():
        if type(parameter) == tuple:
            if len(parameter) == 2 and parameter[0] == 1:
                user_vars.append(1)
            elif len(parameter) == 2 and parameter[0] == 0:
                user_vars.append(0)
            else:
                for elem in parameter:
                    user_vars.append(elem)
        else:
            user_vars.append(parameter)
    return [user_vars]
    # Получить предсказание по заданным пользователем параметрам `user_vars`
    # result = loaded_model.predict(user_vars)
    # return result

# Токен вашего бота
TOKEN = BOT_TOKEN
bot = telebot.TeleBot(TOKEN)

# Список вопросов
questions = [
    {'key': '1. Количество комнат', 'text': 'Введите количество комнат', 'type': int},
    {'key': '2. Площадь кухни', 'text': 'Введите площадь кухни', 'type': float},
    {'key': '3. Жилая площадь', 'text': 'Введите жилую площадь (кухня+комнаты)', 'type': float},
    {'key': '4. Общая площадь', 'text': 'Введите общую площадь', 'type': float},
    {'key': '5. Год постройки', 'text': 'Введите год постройки', 'type': int},
    {
        'key': '6. Есть ли мусоропровод?',
        'text': 'Есть ли мусоропровод?',
        'options': ['Да.', 'Нет.']
    },
    {'key': '7. Количество подъездов', 'text': 'Введите количество подъездов', 'type': int},
    {
        'key': '8. Есть ли газопровод?',
        'text': 'Есть ли газопровод?',
        'options': ['Да.', 'Нет.']
    },
    {'key': '9. Долгота', 'text': 'Введите долготу', 'type': float},
    {'key': '10. Широта', 'text': 'Введите широту', 'type': float},
    {'key': '5. рейтинг', 'text': 'рейтинг', 'type': float},
    {'key': '11. Удалённость от центра города', 'text': 'Введите удалённость от центра города (в км)', 'type': float},
    {'key': '12. Этаж', 'text': 'Введите этаж арендуемого жилья', 'type': int},
    {'key': '13. Число этажей в доме', 'text': 'Введите число этажей в доме', 'type': int},
    {
        'key': '14. Материал покрытий',
        'text': 'Выберите материал перекрытий',
        'options': ['Деревянные', 'Железобетонные', 'Смешанные']
    },
    {
        'key': '15. Материал стен',
        'text': 'Выберите материал стен',
        'options': ['Блочные', 'Деревянные', 'Железобетон', 'Кирпич', 'Монолитные', 'Панельные', 'Смешанные']
    },
    {
        'key': '16. Тип отопления',
        'text': 'Выберите тип отопления',
        'options': [
            'Автономная котельная (крышная, встроенно-пристроенная)',
            'Индивидуальный тепловой пункт (ИТП)',
            'Квартирное отопление (квартирный котел)',
            'Без отопления',
            'Печное',
            'Центральное'
        ]
    },
    {
        'key': '17. Технология строительства дома',
        'text': 'Выберите технологию строительства дома',
        'options': [
            'блок', 'блок-панель', 'ж/б', 'каркас-кирпич',
            'каркас-панель', 'кирпич', 'монолит', 'монолит-кирпич',
            'монолит-панель', 'панель', 'панель-кирпич'
        ]
    }
]

# Хранилище данных
user_data = {}

# Главная клавиатура
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ввести параметры"))
    return markup

# Клавиатура для вопросов
def question_menu(back=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Главное меню"))
    if back:
        markup.add(KeyboardButton("Назад"))
    return markup

# Создать кнопки для вариантов
def create_options_menu(options, back=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        markup.add(KeyboardButton(option))
    markup.add(KeyboardButton("Главное меню"))
    if back:
        markup.add(KeyboardButton("Назад"))
    return markup

# Стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = {'parameters': {}, 'current_index': 0, 'confirming': False, 'correcting': False}
    bot.send_message(
        user_id,
        f'Привет, {message.from_user.first_name}! Я помогу определить цену аренды. Нажмите "Ввести параметры" для начала.',
        reply_markup=main_menu()
    )

# Обработка текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    if text == "Ввести параметры":
        user_data[user_id]['current_index'] = 0
        user_data[user_id]['confirming'] = False
        user_data[user_id]['correcting'] = False
        ask_question(message)
    elif text == "Главное меню":
        start(message)
    elif text == "Назад":
        user_data[user_id]['current_index'] -= 1
        ask_question(message, back=True)
    elif text == "Да":
        if user_data[user_id].get('confirming'):
            print(result(user_data, user_id))
            print(user_data)
            bot.send_message(user_id, f"Квартира будет стоить {loaded_model.predict(result(user_data, user_id))[0]} рублей/месяц.")
            # bot.send_message(user_id, f"Квартира будет стоить asssdd рублей/месяц.")
            start(message)  # Возврат в главное меню
        else:
            bot.send_message(user_id, "Ошибка! Неправильный контекст.")
    elif text == "Нет":
        if user_data[user_id].get('confirming'):
            ask_to_correct(message)
        else:
            bot.send_message(user_id, "Ошибка! Неправильный контекст.")
    elif text.isdigit() and user_data[user_id].get('correcting'):
        correct_index = int(text) - 1
        if 0 <= correct_index < len(questions):
            user_data[user_id]['current_index'] = correct_index
            user_data[user_id]['correcting'] = False
            ask_question(message)
        else:
            bot.send_message(user_id, "Неверный номер вопроса. Попробуйте снова.")
    else:
        process_answer(message)

# Задать вопрос
def ask_question(message, back=False):
    user_id = message.from_user.id
    index = user_data[user_id]['current_index']
    if index < len(questions):
        question = questions[index]
        if 'options' in question:  # Если у вопроса есть варианты
            bot.send_message(
                user_id,
                question['text'],
                reply_markup=create_options_menu(question['options'], back=index > 0)
            )
        else:  # Для обычных вопросов
            bot.send_message(
                user_id,
                question['text'],
                reply_markup=question_menu(back=index > 0)
            )
    else:
        confirm_parameters(message)

# Подтверждение введённых данных
def confirm_parameters(message):
    user_id = message.from_user.id
    summary = "\n".join(
        [f"{key}: {value}" for key, value in user_data[user_id]['parameters'].items()]
    )
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    bot.send_message(
        user_id,
        f"Вот введённые параметры:\n{summary}\nВерны ли они?",
        reply_markup=markup
    )
    user_data[user_id]['confirming'] = True

# Обработать ответ
def process_answer(message):
    user_id = message.from_user.id
    index = user_data[user_id]['current_index']
    question = questions[index]

    # Если у вопроса есть варианты
    if 'options' in question:
        options = question['options']
        if message.text in options:
            # Создаём вектор (0, 0, 0, 1, 0) для выбранного ответа
            answer_vector = [1 if option == message.text else 0 for option in options]
            user_data[user_id]['parameters'][question['key']] = tuple(answer_vector)
            user_data[user_id]['current_index'] += 1
            if user_data[user_id].get('confirming'):
                confirm_parameters(message)
            else:
                ask_question(message)
        else:
            bot.send_message(
                user_id,
                f"Ошибка ввода. Пожалуйста, выберите один из вариантов: {', '.join(options)}",
                reply_markup=create_options_menu(options, back=index > 0)
            )
    else:
        try:
            answer = question['type'](message.text)
            user_data[user_id]['parameters'][question['key']] = answer
            user_data[user_id]['current_index'] += 1
            if user_data[user_id].get('confirming'):
                confirm_parameters(message)
            else:
                ask_question(message)
        except ValueError:
            bot.send_message(
                user_id,
                f"Ошибка ввода. Пожалуйста, повторите: {question['text']}",
                reply_markup=question_menu(back=index > 0)
            )

# Спросить, какой вопрос исправить
def ask_to_correct(message):
    user_id = message.from_user.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i, question in enumerate(questions, start=1):
        markup.add(KeyboardButton(str(i)))
    bot.send_message(user_id, "Какой вопрос нужно исправить?", reply_markup=markup)
    user_data[user_id]['correcting'] = True

# Запуск бота
bot.polling()
