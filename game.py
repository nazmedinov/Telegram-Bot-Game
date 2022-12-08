import language_tool_python
import telebot
from telebot import types


words = set()
marker = True
letters = {}
tool = language_tool_python.LanguageTool('ru-RU')
bot = telebot.TeleBot('5873172071:AAF_QjbyOZG4poRDuyT-IicJhb-Wmf9bJ5I')
need_start = True
k = 0


def check_word(slovo):
    global letters
    global marker
    myletters = letters.copy()
    for word in slovo:
        if word not in myletters.keys() or myletters[word] == 0:
            marker = False
            break
        else:
            myletters[word] = myletters[word]-1


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global need_start
    global words
    words = set()
    if call.data == "Старт":
        bot.send_message(call.message.chat.id, 'Введите начальное слово:')
        bot.register_next_step_handler(call.message, get_word)
    elif call.data == "Правила":
        bot.send_message(call.message.chat.id, 'Правила игры: необходимо из букв начального слова составить как можно больше новых слов.')


@bot.message_handler(commands=['start_game'])
def start(message):
    global need_start
    global k
    k = 0
    need_start = False
    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text='Старт', callback_data='Старт')
    keyboard.add(key_start)
    key_rules = types.InlineKeyboardButton(text='Правила', callback_data='Правила')
    keyboard.add(key_rules)
    bot.send_message(message.chat.id, text='Игра начинается!', reply_markup=keyboard)


def get_word(message):
    global main_st
    main_st = message.text.lower()
    matches = tool.check(main_st)
    if len(matches) > 0 and main_st != 'радиомагнитное':
        bot.send_message(message.chat.id, 'К сожалению, такое слово в словаре не обнаружено!')
        bot.register_next_step_handler(message, get_word)
    else:
        main_st = main_st.lower().strip().split()
        if len(main_st) == 0:
            bot.send_message(message.chat.id, "Введите начальное слово:")
            bot.register_next_step_handler(message, get_word)
        elif len(main_st) > 1:
            bot.send_message(message.chat.id, "Необходимо ввести одно слово!")
            bot.register_next_step_handler(message, get_word)
        else:
            for letter in main_st[0]:
                if letter not in letters.keys():
                    letters[letter] = 1
                else:
                    letters[letter] += 1
            bot.send_message(message.chat.id, "Спасибо! Введите проверяемое слово:")
            bot.register_next_step_handler(message, main_f)


def main_f(message):
    global st
    global marker
    global need_start
    if message.text == "Подсчет!":
        bot.send_message(message.chat.id, f'Всего найдено слов: {len(words)}. Круто!')
        for i in words:
            bot.send_message(message.chat.id, f'{i}')
        need_start = True
    if need_start:
        return
    else:
        st = message.text
        st = st.lower().strip().split()
        slovo = []
        if len(st) == 0:
            bot.register_next_step_handler(message, main_f)
        elif len(st) > 1:
            bot.send_message(message.chat.id, 'Необходимо ввести одно слово!')
            bot.register_next_step_handler(message, main_f)
        else:
            for i in range(len(st[0])):
                slovo += st[0][i]
            check_word(slovo)
            if marker == False:
                marker = True
                bot.send_message(message.chat.id, 'Данное слово не подходит!')
                bot.register_next_step_handler(message, main_f)
            else:
                itog = ''
                for letter in slovo:
                    itog = itog + letter
                if itog in words:
                    bot.send_message(message.chat.id, 'Данное слово уже было отгадано!')
                    bot.register_next_step_handler(message, main_f)
                else:
                    matches = tool.check(itog)
                    if len(matches) > 0:
                        bot.send_message(message.chat.id, 'К сожалению, такое слово в словаре не обнаружено!')
                        bot.register_next_step_handler(message, main_f)
                    else:
                        words.add(itog)
                        bot.send_message(message.chat.id, f'Отлично! Отгадано слово: {itog}')
                        bot.register_next_step_handler(message, main_f)

            if len(words) == 1:
                keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                key_stop = types.KeyboardButton('Подсчет!')
                keyboard2.add(key_stop)
                bot.send_message(message.chat.id, text='Вы всегда можете закончить игру, нажав на кнопку Подсчет', reply_markup=keyboard2)


bot.polling(none_stop=True, interval=0)
