from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime
from config import token 
import random
import logging
import sqlite3

connect  = sqlite3.connect("users.db")
cursor = connect.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS clients(
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name VARCHAR(255),    
    last_name VARCHAR(255),
    date_joined DATATIME
);
''')
connect.commit()
class OrderFoodState(StatesGroup):
    name = State()
    title = State()
    phone_number = State()
    address = State()


storage = MemoryStorage()

bot = Bot(token)
dp = Dispatcher(bot,storage=storage)
logging.basicConfig(level=logging.INFO)

start_buttons =[            
    types.KeyboardButton('Меню'),
    types.KeyboardButton('О нас'),
    types.KeyboardButton('Адрес'),
    types.KeyboardButton('Заказать еду')
]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buttons)

@dp.message_handler(commands='start')
async def play(message:types.Message):
    cursor=connect.cursor()
    cursor.execute(f"SELECT id FROM clients WHERE id = {message.from_user.id};")
    res = cursor.fetchall()
    if not  res:
        cursor.execute(f"""INSERT INTO clients (id, username, first_name, last_name, date_joined) VALUES (
            {message.from_user.id},
            '{message.from_user.first_name}',
            '{message.from_user.last_name}',
            '{message.from_user.username}',
            '{datetime.now()}'
        );
        """)
        cursor.connection.commit()
    await message.answer(f"Здраствуйте {message.from_user.full_name}",reply_markup=start_keyboard)


@dp.message_handler(text="О нас")
async def about_us(message:types.Message):
    await message.reply("Кафе Ожак Кебаб славится своей кухней. Лучшие традиции турецкой кухни по доступным ценам.") 

@dp.message_handler(text='Меню')
async def menu(message:types.Message):
    await message.answer("Посмотрите наше меню: [ссылка](https://nambafood.kg/ojak-kebap)", 
    parse_mode=types.ParseMode.MARKDOWN)

@dp.message_handler(text="Адрес")
async def adres(message:types.Message):
    await message.reply("Наш адрес: Курманжан датка, 89")
    await message.answer_location(40.51210975295718, 72.8069874111937)


@dp.message_handler(text='Заказать еду')
async def order_foor(message:types.Message):
    await message.answer(f"Введите свое имя ")
    await OrderFoodState.name.set()

@dp.message_handler(state=OrderFoodState.name)
async def ordes(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer("Что хотите заказать? ")
    await OrderFoodState.next()

@dp.message_handler(state=OrderFoodState.title)
async def ordes(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await message.answer("Введите свой номер телефона? ")
    await OrderFoodState.next()

import re

@dp.message_handler(state=OrderFoodState.phone_number)
async def process(message: types.Message, state: FSMContext):
    phone_number = message.text

    # Проверка номера телефона с использованием регулярного выражения
    if re.match(r'^\+?\d{1,3}?\d{9,15}$', phone_number):
        async with state.proxy() as data:
            data['phone_number'] = phone_number

        await message.answer("Введите свой адрес")
        await OrderFoodState.next()
    else:
        await message.answer("Некорректный номер телефона. Пожалуйста, введите корректный номер.")


@dp.message_handler(state=OrderFoodState.phone_number)
async def process(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await message.answer("Введите свой адрес")
    await OrderFoodState.next()




executor.start_polling(dp)