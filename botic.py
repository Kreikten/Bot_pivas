import logging

#import states as states
from aiogram import Bot, Dispatcher, executor, types
import bs4
import requests
import sqlite3
import asyncio
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from main import STATES, checkAccess
from aiogram.dispatcher.filters import Text

class TestStates(Helper):
    mode = HelperMode.snake_case
    S_ENTER_LOGIN = ListItem()
    S_ENTER_PASS =  ListItem()
    S_GET_INFO =  ListItem()
    S_DEFAULT = ListItem()

class BotDB:

    def _init_(self, db_file,tg_id, state):
        """Подключить бд"""
        self.conn=sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS 'user_states' ('tg_id' TEXT, 'states' INTEGER)",(tg_id, state,)),


    def get_user_id(self, tg_id):
        """Получить текущее состояние пользователя - принимает тг айди, возвращает состояние"""
        tg_id = bot.get_me(self)
        self.cursor.execute("INSERT INTO 'users_states' ('tg_id') VALUES ('tg_id')", (tg_id,))
        result = self.cursor.execute("SELECT 'states' FROM 'users_states' WHERE 'tg_id' = ?", (tg_id,))
        return self.conn.commit()

    def get_user_state(self, states):
        """Получаем те6кущее состояние пользователя"""
        self.cursor.execute("INSERT INTO 'users_states' ('states') VALUES (?)", (states,))
        return self.conn.commit()

    def add_record(self, tg_id, states):
        """Записать новое сосотояние пользователя - принимает тг айди и состояние, возвращает ничего"""
        self.cursor.execute("INSERT INTO 'user_states' ('tg_id','states' ) VALUES (?,?)",(tg_id,states,))
        return self.conn.commit()

    def get_records(self,tg_id,states):
        """Получить все записи из БД-получает ничего, возвращает записи"""
        result = self.cursor.execute("SELECT tg_id, states FROM user_states;"),
        self.get_user_id(tg_id,states),
        return result.fetcall()

    def update_record(self, tg_id, states):
        """Обновить текущее состояние пользователя - принимает тг айди и состояние, возвращает ничего"""
        tg_id = bot.get_me(self)
        self.cursor.execute("INSERT INTO 'users_states' ('tg_id') VALUES ('tg_id')", (tg_id,))
        self.cursor.execute("INSERT INTO 'user_states' ('states') VALUES ('states')",(states,))
        self.cursor.execute("UPDATE 'user_states' set states = ? where id = ?)",(tg_id,states,))
        return self.conn.commit(),
        print("Запись успешно обновлена")

    def delete_records(self,tg_id):
        """Удаление пользователей из базы"""
        self.cursor.execute("Delete FROM user_states WHERE tg_id='Oleynikov Vitaly Sergeevich';")
        return self.conn.commit()

    def close(self):
            """Закрытие соединения с БД"""
            self.conn.close()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


bot = Bot(token="5282844089:AAHh_Ou1dwd5A4dtztuqTUVJLvcz6lT8QxI")
# Диспетчер для бота
dp = Dispatcher(bot, storage = MemoryStorage())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
for i in range (0, len(TestStates.all())):
    print(TestStates.all()[i])

async def get_current_state(user_id):

    try:
        for name in STATES:
            if name.value == user_id:
                return name.value
                break
    except KeyError:  # Если такого ключа почему-то не оказалось
        return STATES.S_START.value


async def set_state(user_id, value):
    global current_user_state
    try:
        current_user_state = value
        return True
    except Exception as E:

        return False




async def send_message(telebot_client, chat_id, text):
    '''Функция для отправки сообщений
    client - клиент бота
    chat_id - чат, куда отправляем сообщение
    text - текст сообщения
    '''
    telebot_client.send_message(chat_id, text, parse_mode = 'HTML')


@dp.callback_query_handler(Text(startswith='test_'), state=TestStates.S_GET_INFO[0])
async def calll(call:types.CallbackQuery):
    res = call.data.split('_')[1]
    state = dp.current_state(user=call.from_user.id)
    dict = await state.get_data()
    print(dict, res)
    try:
        if call.message:
            if dict['authentificated']:
                # keyboard (Работа с кнопками под текстом)
                if res == '1':
                    await call.message.answer('Температура...')
                elif  res =='2':
                    await call.message.answer('*Влажность...*')
                elif res =='3':
                    await call.message.answer('*Воздух...*')
                elif res =='4':
                    await call.message.answer('*Кол-во...*')
                elif res =='5':
                    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
                    response1 = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")

                    if response.status_code == 200:
                        content = response.json()
                        content1 = response1.json()
                        await call.message.answer(
                                           'Курс доллара: ' + str(content["Valute"]["USD"]['Value']) +
                                           '\n' + 'Курс евро: ' + str(
                                               content["Valute"]["EUR"]['Value']) + '\nКурс Bitcoin: ' +
                                           str(content1['bpi']['USD']['rate_float']))
                elif res =='6':
                    s = requests.get('http://anekdotme.ru/random')
                    b = bs4.BeautifulSoup(s.text, "html.parser")
                    p = b.select('.anekdot_text')
                    for x in p:
                        s = (x.getText().strip())
                        await call.message.answer( s)
                        break
                elif res =='7':
                    response = requests.get("https://beer-501.herokuapp.com/beer/getAll")
                    print(response)
                    if response.status_code == 200:
                        content = response.json()
                        print(content)

                        for elem in content:
                            s = ''
                            s += str(elem['name_beer']) + ' - '
                            s += str(elem['value_beer']) + ' л' + '\n'
                            await call.message.answer(s)
            else:
                await call.message.answer('Авторизуйтесь для получения информации')
    except Exception as E:
        print(E)


@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message):
 #   tg_id = BotDB.get_user_id(tg_id='@...')
   # if tg_id["tg_id"] != 'left':
   #         await bot.send_message(message.from_user.id, 'Привет, {0.first_name}👋🏻 \n...'.format(message.from_user)),
   # else:
    #          await bot.send_message(message.from_user.id, 'Ласкаво просимо!')
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[0])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/help")
    item2 = types.KeyboardButton("/login")
    item3 = types.KeyboardButton("/info")
    item4 = types.KeyboardButton("/reset")
    markup.add(item1, item2, item3, item4)
    await message.reply('Хай', parse_mode='html', reply_markup = markup)

    #set_state(current_user_id, 1)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@dp.message_handler(commands=["reset"], state="*")
async def cmd_reset(message):
    # States
    #BotDB.add_record('0',states)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/help")
    item2 = types.KeyboardButton("/login")
    item3 = types.KeyboardButton("/info")
    item4 = types.KeyboardButton("/reset")
    markup.add(item1, item2, item3, item4)
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[0])
    await message.reply("Начнём по новой", reply_markup=markup)



@dp.message_handler(commands=["help"], state="*")
async def cmd_reset(message):
    current_chat_id = message.chat.id

    await message.reply("Команды:\n1./login - авторизация\n2. /help - список команд\n3. "
                                          "/reset - возврат в начальное состояние\n4. "
                                          "/info - текущий статус и получение информации по возможности")

@dp.message_handler(commands=["info"], state="*")
async def cmd_reset(message:types.Message):
    state = dp.current_state(user=message.from_user.id)
    dict = state.get_data()
    print(dict)
    if dict['authenthificated']:
        await message.reply(text='Бот предназначен для управления пивной лавкой. '
                                 'На данный момент вы авторизованы и можете получить данные')
        markup1 = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(text="Данные с датчика температуры", callback_data='test_1')
        item2 = types.InlineKeyboardButton(text="Данные с датчика влажности", callback_data='test_2')
        item3 = types.InlineKeyboardButton(text="Качество воздуха", callback_data='test_3')
        item4 = types.InlineKeyboardButton(text="Количество посетителей ", callback_data='test_4')
        item5 = types.InlineKeyboardButton(text="Курс доллара ", callback_data='test_5')
        item6 = types.InlineKeyboardButton(text="Анекдот", callback_data='test_6')
        item7 = types.InlineKeyboardButton(text="Проверить наличие пива", callback_data='test_7')
        #
        markup1.add(item1, item2, item3, item4, item5, item6,item7)
        #
        await message.reply('Выберите интересующую вас информацию:',
                            parse_mode='html', reply_markup=markup1)
    else:
        await message.reply(
                     'Бот предназначен для управления пивной лавкой. На данный момент вы не авторизованы.'
                     ' Отправьте команду "/login" для авторизации.')


@dp.message_handler(state=TestStates.S_ENTER_LOGIN)
async def user_entering_name(message: types.Message):
    print('1')

    state = dp.current_state(user=message.from_user.id)
    print('2')
   # print(state.get_state())
    await state.update_data(login=message.text.lower())
    await state.set_state(TestStates.all()[2])
    await message.reply("Логин получен, введите пароль")


@dp.message_handler(state=TestStates.S_ENTER_PASS[0])
async def user_entering_pass(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(passwd=message.text.lower())
    dict = await state.get_data()
    print(dict)
    login = dict['login']
    passwd = dict['passwd']
    # В случае с именем не будем ничего проверять, пусть хоть "25671", хоть Евкакий
    await message.reply("Принято, идёт проверка...")
    if checkAccess(login, passwd):
        await message.reply('Авторизация прошла успешно! Добро пожаловать')

        await state.update_data(authentificated=True)
        print(await state.get_data())
        print(TestStates.all()[3])
        await state.set_state(TestStates.all()[3])
        markup1 = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(text="Данные с датчика температуры", callback_data='test_1')
        item2 = types.InlineKeyboardButton(text="Данные с датчика влажности", callback_data='test_2')
        item3 = types.InlineKeyboardButton(text="Качество воздуха", callback_data='test_3')
        item4 = types.InlineKeyboardButton(text="Количество посетителей ", callback_data='test_4')
        item5 = types.InlineKeyboardButton(text="Курс доллара ", callback_data='test_5')
        item6 = types.InlineKeyboardButton(text="Анекдот", callback_data='test_6')
        item7 = types.InlineKeyboardButton(text="Проверить наличие пива", callback_data='test_7')
        #
        markup1.add(item1, item2, item3, item4, item5, item6, item7)
        #
        await message.reply('Выберите интересующую вас информацию:',
                            parse_mode='html', reply_markup=markup1)
        # States
        # BotDB.add_record('3', states)
    else:
        await message.reply('Ошибка авторизации. Отправьте в следующем сообщении логин.')
        await state.set_state(TestStates.all()[1])
        # States
        # BotDB.add_record('1', states)


@dp.message_handler(commands=["login"], state = '*')
async def cmd_reset(message:types.Message):
   # BotDB.add_record('1')
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[1])
    await message.reply( 'В следующем сообщении введите логин')




#def main():

    #bot.infinity_polling( interval=0)



#if __name__ == '__main__':
 #   try:
  #      main()
   # except Exception as E:
   #     print(E)


if __name__ == "__main__":
# Запуск бота
    try:
        executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
    except Exception as E:
        print(E)