import openai
import telebot
from secret import tg_token, proxyapi_key


# подключение к Telegram API
bot = telebot.TeleBot(tg_token)


# подключение к OpenAI API через ProxyAPI
client = openai.OpenAI(api_key=proxyapi_key,
                       base_url='https://api.proxyapi.ru/openai/v1')


# создание команды /start
@bot.message_handler(commands=['start'])
def start(message):
    start_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    text_key = telebot.types.KeyboardButton(text='Начать диалог с ботом')
    image_key = telebot.types.KeyboardButton(text='Сгенерировать изображение')
    help_key = telebot.types.KeyboardButton(text='Помощь')
    start_keyboard.add(text_key, image_key, help_key)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Я искусственный интеллект NeuroBoy. Я могу общаться с Вами или генерировать изображения. Также меня можно добавить в групповой чат. Используйте кнопки или команды для взаимодействия с ботом.', reply_markup=start_keyboard)
    
    @bot.message_handler(content_types=['text'])
    def start_handler(message):
        if message.text == 'Начать диалог с ботом':
            text(message)
        if message.text == 'Сгенерировать изображение':
            image(message)
        if message.text == 'Помощь':
            help_func(message)


# создание команды /help
@bot.message_handler(commands=['help'])
def help_func(message):
    bot.send_message(message.chat.id, 'Вот что я умею:\n\n/start - запустить бота;\n/help - помощь;\n/text - начать диалог с ботом;\n/image - сгенерировать изображение.\n\n❗ Для корректной работы бота в групповом чате, пожалуйста, наделите его правами администратора ❗\n\nОжидание ответа от бота может быть достаточно длительным. Наберитесь терпения!\n\nПо всем вопросам Вы можете писать сюда: @Nikitos_Pan', reply_markup=telebot.types.ReplyKeyboardRemove())


# создание команды /text через две функции: text() и chat()
@bot.message_handler(commands=['text'])
def text(message):
    bot.send_message(message.chat.id, 'Чем я могу Вам помочь?', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, chat)

def chat(message):
    if message.text != None:
        try:
            match message.text:
                case '/start':
                    start(message)
                case '/help':
                    help_func(message)
                case '/text':
                    text(message)
                case '/image':
                    image(message)
                case '/start@neurochatboy_bot':
                    start(message)
                case '/help@neurochatboy_bot':
                    help_func(message)
                case '/text@neurochatboy_bot':
                    text(message)
                case '/image@neurochatboy_bot':
                    image(message)
                case _:
                    chat_completion = client.chat.completions.create(model='gpt-4o-mini', 
                                                                     messages=[{'role': 'user', 'content': message.text}],
                                                                     max_tokens=500)
                    
                    # обработка ответа LLM
                    llm_answer = str(chat_completion)

                    if "message=ChatCompletionMessage(content='" in llm_answer:
                        llm_answer = llm_answer.split("message=ChatCompletionMessage(content='")[1]
                        llm_answer = llm_answer.split("', role='assistant'")[0]

                    else:
                        llm_answer = llm_answer.split('message=ChatCompletionMessage(content="')[1]
                        llm_answer = llm_answer.split("""", role='assistant'""")[0]

                    llm_answer = llm_answer.replace('\u005cn', '\n')
                    
                    bot.send_message(message.chat.id, llm_answer)
                    bot.register_next_step_handler(message, chat)

        except telebot.apihelper.ApiTelegramException as e:
            bot.send_message(message.chat.id, 'Напишите что-нибудь другое.')
            bot.register_next_step_handler(message, chat)
            print(e)

        except openai.APIStatusError as e:
            bot.send_message(message.chat.id, 'К сожалению, на данный момент у бота закончились деньги и пока он не сможет Вам ответить. Вы можете написать разработчику с просьбой о восстановлении работоспособности бота: @Nikitos_Pan')
            print(e)

    else:
        bot.send_message(message.chat.id, 'Напишите что-нибудь другое.')
        bot.register_next_step_handler(message, chat)



# создание команды /image через две функции: image() и generate_image()
@bot.message_handler(commands=['image'])
def image(message):
    bot.send_message(message.chat.id, 'Пожалуйста, опишите картинку (для повышения точности Вы можете сделать это на английском языке).', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, generate_image)

def generate_image(message):
    if message.text != None:
        try:
            match message.text:
                case '/start':
                    start(message)
                case '/help':
                    help_func(message)
                case '/text':
                    text(message)
                case '/image':
                    image(message)
                case '/start@neurochatboy_bot':
                    start(message)
                case '/help@neurochatboy_bot':
                    help_func(message)
                case '/text@neurochatboy_bot':
                    text(message)
                case '/image@neurochatboy_bot':
                    image(message)
                case _:
                    generated_image = client.images.generate(prompt=message.text, n=1, size='256x256', model='dall-e-2')

                    # обработка ответа LLM
                    image_url = str(generated_image)
                    image_url = image_url.split(", url='")[1]
                    image_url = image_url.removesuffix("')])")

                    bot.send_photo(message.chat.id, image_url)

        except telebot.apihelper.ApiTelegramException as e:
                bot.send_message(message.chat.id, 'Напишите что-нибудь другое.')
                bot.register_next_step_handler(message, generate_image)
                print(e)

        except openai.APIStatusError as e:
                bot.send_message(message.chat.id, 'К сожалению, на данный момент у бота закончились деньги и пока он не сможет Вам ответить. Вы можете написать разработчику с просьбой о восстановлении работоспособности бота: @Nikitos_Pan')
                print(e)

    else:
        bot.send_message(message.chat.id, 'Напишите что-нибудь другое.')
        bot.register_next_step_handler(message, generate_image)


# добавление списка комманд
def set_commands():
    commands = [telebot.types.BotCommand(command='/start', description='Запустить бота'), 
                telebot.types.BotCommand(command='/help', description='Помощь'), 
                telebot.types.BotCommand(command='/text', description='Начать диалог с ботом'), 
                telebot.types.BotCommand(command='/image', description='Сгенерировать изображение')]
    bot.set_my_commands(commands)
set_commands()


# запуск бота
bot.polling(non_stop=True, interval=0)