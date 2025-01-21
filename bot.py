import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import openai
from bot_keys import *

# Настройка OpenAI API
openai.api_key = API_KEY

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

user_context = {}  # Словарь с контекстом


# Функция для обращения к OpenAI
def get_gpt_response(user_message, system_prompt):
    try:
        # Запрос к модели
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,  # Увеличьте, если нужны более длинные ответы
            temperature=0.7,  # Креативность
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Ошибка GPT: {e}"


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, использующий GPT для упрощения "
                          "текстов законов. Напишите мне текст, и я перепишу его.")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_message = message.text
    username = message.from_user.username

    if username not in user_context:
        user_context[username] = []

    user_context[username].append(message.text)
    context = " ".join(user_context[username][-3:])  # Храним только последние 3 сообщения

    if user_message == "Очистить контекст":
        # Очищение контекста
        user_context[message.from_user.username] = []
        bot.reply_to(message, "Контекст сброшен.")
    elif user_message == 'Объяснить термины':
        system_prompt = (
            'Добавь список сложных терминов из твоего предыдущего'
            ' ответа с их краткими определениями. Например: '
            '<i>Термин:</i> Конституция — основной закон государства.'
        )

        bot.reply_to(message, "Подождите, думаю...")
        response = get_gpt_response(context, system_prompt)

        # Логирование
        with open('запросы.txt', 'a') as responses:
            responses.write(f'{username}:\n{user_message}\n\nbot:\n{response}\n-\n-\n')
        print(response)

        # Создание клавиатуры
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Очистить контекст"))
        markup.add(KeyboardButton("Объяснить термины"))

        bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=markup)
    else:
        # Описание контекста для модели
        system_prompt = (
            "Вы эксперт, который помогает переписывать тексты законов, делая их простыми, ясными и доступными для широкой "
            "аудитории, не обладающей юридическими знаниями. Сохраняйте ключевые аспекты и суть закона, избегая сложных "
            "формулировок и юридического жаргона. Включайте пояснения сложных моментов и примеры (в формате: <i>Пример:</i>). "
            "Также форматируй текст в формате: <b>Заголовок</b> "
            "Это пример текста, в котором <b>жирный текст</b>, <i>курсивный текст</i>, <s>зачёркнутый текст</s>, "
            "<u>подчёркнутый текст</u> и <code>код</code> вместо ``` и ** оформлены в соответствии с указанным форматом."
        )
        bot.reply_to(message, "Подождите, думаю...")
        response = get_gpt_response(context, system_prompt)

        # Логирование
        with open('запросы.txt', 'a') as responses:
            responses.write(f'{username}:\n{user_message}\n\nbot:\n{response}\n-\n-\n')
        print(response)

        # Создание клавиатуры
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Очистить контекст"))
        markup.add(KeyboardButton("Объяснить термины"))

        bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=markup)


# Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)