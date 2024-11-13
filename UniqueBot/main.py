import asyncio

MY_TOKEN = "6615733860:AAHKJZNX9U6IbZaPsk24RZ2_YU_U1VSMxDo"

import datetime
import requests
import schedule
import logging
from database import add_user, enable_notifications, disable_notifications
import math
import time
from aiogram import Bot, Dispatcher, types
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

    # Сохраняем user_id в состоянии
    await dp.current_state(user=message.from_user.id).update_data(user_id=message.from_user.id)



@dp.message_handler(lambda message: message.text and ':' in message.text)
async def save_notification_time(message: types.Message):
    user_data = await dp.current_state(user=message.from_user.id).get_data()
    user_id = user_data.get('user_id')

    if user_id:
        try:
            time_, city = message.text.split(maxsplit=1)
            await enable_notifications(user_id, city, time_)
            photo = open('On.jpg', 'rb')
            await bot.send_photo(message.chat.id, photo)
            await message.reply(f"Оповещение о погоде включено на {time_} для города {city}.")


        except ValueError:
            await message.reply("Неверный формат. Пожалуйста, введите время в формате HH:MM и название города.")
    else:
        await message.reply("Сначала активируйте оповещение.")


@dp.message_handler(Text(equals="Выключить оповещение о погоде"))
async def OFFNotification(message: types.Message):
    user_data = await dp.current_state(user=message.from_user.id).get_data()
    user_id = user_data.get('user_id')
    await disable_notifications(user_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Включить оповещение о погоде"]
    keyboard.add(*buttons)

    await message.reply("Уведомления выключены!", reply_markup=keyboard)


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

async def send_message():
    print("Отправка сообщения пользователю %s...", 830637790)
    await bot.send_message(830637790, "Привет! Это запланированное сообщение.")
    print("Сообщение успешно отправлено!")


async def schedule_task():
    # Получаем текущее время
    now = time.localtime()

    # Определяем время запуска задачи
    hour = 20
    minute = 52

    if now.tm_hour > hour or (now.tm_hour == hour and now.tm_min >= minute):
        # Если текущее время больше 15:00, планируем задачу на завтра
        tomorrow = time.time() + 24 * 60 * 60
        tomorrow_time = time.localtime(tomorrow)

        schedule_time = f"{tomorrow_time.tm_year}-{tomorrow_time.tm_mon}-{tomorrow_time.tm_mday} {hour}:{minute}"
        print(f"Планирование задачи на {schedule_time}")
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(send_message)
    else:
        # Иначе планируем задачу на сегодня
        today_time = f"{now.tm_year}-{now.tm_mon}-{now.tm_mday} {hour}:{minute}"
        print(f"Планирование задачи на {today_time}")
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(send_message)



# Основной блок программы
async def main():
    await schedule_task()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
