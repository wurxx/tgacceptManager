from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import *
from aiogram.types import *
from keyboards import *



startKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить аккаунт', callback_data='addTgacc'), InlineKeyboardButton(text='Мои аккаунты', callback_data='MyTgacc')],
    # [InlineKeyboardButton(text='Обновить интервал', callback_data='updateInterval')],
    # [InlineKeyboardButton(text='Тексты', callback_data='myTexts')]
    ])


cancelKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
    ])