from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import *
from aiogram.types import *
from keyboards import *



startKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить аккаунт', callback_data='addTgacc')]
    ])


cancelKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
    ])