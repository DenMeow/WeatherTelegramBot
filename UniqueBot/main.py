MY_TOKEN = "6615733860:AAHKJZNX9U6IbZaPsk24RZ2_YU_U1VSMxDo"

import datetime
import requests
import logging
from database import init_db, add_user, enable_notifications, disable_notifications
import math
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text


logging.basicConfig(level=logging.INFO)

bot = Bot(token=MY_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Сохраняем пользователя в БД
    await add_user(user_id, username, first_name, last_name)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Включить оповещение о погоде"]
    keyboard.add(*buttons)
    photo = open('hi.jpg', 'rb')
    await bot.send_photo(message.chat.id, photo)
    await message.answer(f"Привет, {message.from_user.first_name} \nНапиши мне название города и я пришлю сводку погоды🙂", reply_markup=keyboard)

@dp.message_handler(Text(equals="Включить оповещение о погоде"))
async def OnNotification(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Выключить оповещение о погоде"]
    keyboard.add(*buttons)

    await message.reply("Введите время в формате HH:MM и название города (например, 14:30 Москва):", reply_markup=keyboard)
    # Сохраняем user_id для дальнейшего использования
    await dp.current_state(user=message.from_user.id).set_data({'user_id': message.from_user.id})

@dp.message_handler(Text(equals="Выключить оповещение о погоде"))
async def OFFNotification(message: types.Message):
    await message.reply("Уведомления выключены!")

    user_data = await dp.current_state(user=message.from_user.id).get_data()
    user_id = user_data.get('user_id')
    await disable_notifications(user_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Включить оповещение о погоде"]
    keyboard.add(*buttons)

@dp.message_handler()
async def get_weather(message: types.Message):
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&lang=ru&units=metric&appid=1d0e19233121ae2aeb9360c2328ef631")
        data = response.json()
        city = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        # продолжительность дня
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        code_to_smile = {
            "Clear": "Ясно ☀️",
            "Clouds": "Облачно 🌥️",
            "Rain": "Дождь ☔️",
            "Drizzle": "Дождь 🌧️",
            "Thunderstorm": "Гроза 🌩️",
            "Snow": "Снег ❄️",
            "Mist": "Туман 🌫️"
        }
        # значение погоды
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            # если эмодзи для погоды нет
            wd = "Посмотри в окно, я не понимаю, что там за погода..."

        await message.reply(f"Погода в городе: {city}\nТемпература: {cur_temp}°C {wd}\n"
            f"Влажность: {humidity}%\nДавление: {math.ceil(pressure / 1.333)} мм.рт.ст\nВетер: {wind} м/с \n"
            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
            f"Хорошего дня!"
        )

    except:
        await message.reply("Проверьте название города!")


if __name__ == '__main__':
    from asyncio import run

    async def on_startup(dp):
        await init_db()

    run(executor.start_polling(dp, on_startup=on_startup))