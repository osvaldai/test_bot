import logging

from aiogram import *
from aiogram.types import *
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import os
from database import *

API_TOKEN = '2063536896:AAEV3dvUsgbUET1e5mKkw4vLM05qFhFkUBk'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# создаём форму и указываем поля
class Form(StatesGroup):
    name = State()
    title = State()
    description = State()
    dt = State()



keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_1 = KeyboardButton(text='Каталог')
menu_2 = KeyboardButton(text='Добавить событие')
keyboard.add(menu_1, menu_2)

data_names = 'devs.db'
name_tables = 'devs'

dbs = SQLighter (data_names, name_tables)


bt1 = InlineKeyboardButton(text='Посмотреть событие', callback_data='see')
bt2 = InlineKeyboardButton(text='Посмотреть следующие событие', callback_data='next')
bt3 = InlineKeyboardButton(text="Удалить событие", callback_data='del')
inkey = InlineKeyboardMarkup(row_width=1)

dt_id = 0


@dp.callback_query_handler(text="see")
async def send_random_value(call: types.CallbackQuery):
    info = 'Ваше событие: \n' \
           'Название: %(name)s \n' \
           'Заголовок: %(title)s\n' \
           'Описание: %(desc)s\n' \
           'Дата: %(dat)s' % {'name': dbs.get_devs (dt_id)[1],
                              'title': dbs.get_devs (dt_id)[2],
                              'desc': dbs.get_devs (dt_id)[3],
                              'dat': dbs.get_devs (dt_id)[4]}
    # await call.message.answer(info)

    await call.message.answer(info, reply_markup=InlineKeyboardMarkup(row_width=1).add(bt2))


@dp.callback_query_handler (text="next")
async def send_random_value(call: types.CallbackQuery):
    dt_id_1 = dt_id
    dt_id_1 += 1
    info = 'Ваше событие: \n' \
           'Название: %(name)s \n' \
           'Заголовок: %(title)s\n' \
           'Описание: %(desc)s\n' \
           'Дата: %(dat)s' % {'name': dbs.get_devs (dt_id_1)[1],
                              'title': dbs.get_devs (dt_id_1)[2],
                              'desc': dbs.get_devs (dt_id_1)[3],
                              'dat': dbs.get_devs (dt_id_1)[4]}
    dt_id_1 += 1
    await call.message.answer(text=info, reply_markup=InlineKeyboardMarkup(row_width=1).add(bt2))



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    await message.answer ("Добро пожаловать, {}".format (message.chat.full_name), reply_markup=keyboard)


@dp.message_handler(text=['Каталог'])
async def catalog(message: types.Message):

    txt = str(*dbs.number_events())

    await message.answer('У вас событий: ' + txt, reply_markup=inkey.add(bt1))



@dp.message_handler(text=['Добавить событие'])
async def add_devs(message: types.Message):
    await Form.name.set()
    await message.answer('Напишите имя события: ')


# Сюда приходит ответ с именем
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Напишите Заголовок: ")


# Принимаем Заголовок и узнаем описание
@dp.message_handler(lambda message: message.text, state=Form.title)
async def process_desc(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(title=message.text)

    await message.reply ("Укажите описание события: ")


# Принимаем описание и узнаём дату
@dp.message_handler(lambda message: message.text, state=Form.description)
async def process_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await Form.next()

    await message.reply("Укажи дату в формате 2021-12-25: ")


# Сохраняем дату, выводим информацию по событию
@dp.message_handler(state=Form.dt)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dt'] = message.text
        # markup = types.ReplyKeyboardRemove()
        dbs.add_devs(data['name'], data['title'], data['description'], data['dt'])

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Событие успешно создано!!\n Имя события: ', data['name']),
                md.text('Заголовок: ', data['title']),
                md.text('Описание: ', data['description']),
                md.text('Дата: ',data['dt']),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )

    await state.finish()




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

