import asyncio
import os
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram import filters
from pyrogram.types import Message
import aiohttp
from config import *
import logging
# logging.basicConfig(level=logging.INFO)
# Функция для выбора случайного приветственного сообщения
states = []
async def get_random_welcome_message(phone):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"http://{HOST}/texts?phone={phone}") as r:
            if r.status != 200:print("Ошибка при запросе, текст отсутствует");return defaultMessage
            return random.choice(await r.json())[0]


async def check_client_status(channel_id, client):
    try:
        chat_member = await client.get_chat_member(channel_id, "me")
        return chat_member.status
    except Exception as e:
        print(f"Ошибка при проверке статуса: {e}")
        return None


async def approve_and_welcome_users(client:Client, channelID):
        states.append(client.phone_number)
    # """
        # Одобряет заявки на вступление в канал и отправляет приветственные сообщения.
        # """
        # async with aiohttp.ClientSession() as s:
        #     async with s.get(f"http://{HOST}/Accs") as r:
        #         if r.status != 200:print("Ошибка при запросе, клиент отсутствует")
        #         myAcc = random.choice(await r.json())
        async with client:        
                
            [await client.get_chat(x.chat.id) async for x in client.get_dialogs() if x.chat.id == channelID]
            
            status = await check_client_status(channelID, client)
            if status != ChatMemberStatus.ADMINISTRATOR:
                print("Клиент не является администратором канала. Завершение работы.")
                states.remove(client.phone_number)
                return

            try:
                async for request in client.get_chat_join_requests(channelID):
                    user_id = request.user.id
                    
                    print(f"Одобряем заявку пользователя {user_id}")
                    await client.approve_chat_join_request(channelID, user_id)

                    try:
                        welcome_message = await get_random_welcome_message(client.phone_number)
                        print(f"Отправляем сообщение пользователю {user_id}")
                        await client.send_message(user_id, welcome_message)
                        
                    except Exception as e:
                        print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            except FloodWait as flood:
                print(f"Слишком много запросов. Ожидаем {flood.value} секунд.")
                await asyncio.sleep(flood.value)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                
        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://{HOST}/interval?phone={client.phone_number}") as r:
                if r.status != 200:print("Ошибка при запросе, интервал отсутствует")
                print(await r.json())
                interval = [int(x) for x in ''.join((await r.json())[0][0]).split("-")]
                print(interval)
                
        await asyncio.sleep(random.randint(min(interval), max(interval)))
        states.remove(client.phone_number)

        
            

async def main():
    """
    Основной процесс запуска клиента и планировщика.
    """
    print("Запуск клиента Pyrogram...")
    tasks = []
    while True:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://{HOST}/Accs") as r:
                if r.status != 200:print('Ошибка при отправке запроса')
                myAccs = await r.json()
                print(myAccs)
        for acc in myAccs:
            if acc[2] not in states:tasks.append(asyncio.create_task(approve_and_welcome_users(Client(f"./sess/{acc[2]}", acc[0], acc[1], phone_number=acc[2], password=acc[3]), acc[-1])) )
        
        await asyncio.sleep(5)
    


async def handle_private_message(client: Client, message: Message):
    if message.chat.type != ChatType.PRIVATE: print(message);return
    """
    Обработчик входящих сообщений.
    """
    print(f"Получено сообщение от {message.from_user.id}: {message.text}")
    await message.reply("Спасибо за ваше сообщение! Мы скоро ответим.")


if __name__ == "__main__":
    asyncio.run(main())  # Запуск asyncio.run только для основной функции
