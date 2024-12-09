from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import *
from aiogram.types import *
from aiogram.fsm.state import *
from aiogram.fsm.context import *
from keyboards import *
from pyrogram import Client
import aiofiles
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid
from aiogram.types import FSInputFile

bot = Bot(token='yourToken', default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class AddTelegramAccount(StatesGroup):
    phone = State()
    code = State()
    twofuck = State()

db = {}
    
startmesg = '😈' # startMessage
@dp.message(CommandStart())
async def startmsg(message:Message):
    await message.answer(text=startmesg, reply_markup=startKB)

@dp.callback_query(F.data == 'cancel')
async def goHome(callback:CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.answer()
    try:await callback.message.delete()
    except:pass
    await bot.send_message(callback.from_user.id,startmesg, reply_markup=startKB)


@dp.callback_query(F.data == 'addTgacc', StateFilter(default_state))
async def startAddTgAcc(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text('Введите номер в формате 7900*******', reply_markup=cancelKB)
    await state.set_state(AddTelegramAccount.phone)
@dp.message(StateFilter(AddTelegramAccount.phone))
async def addingTGphone(message:Message, state:FSMContext):
    await state.update_data(phone = message.text)
    try:await message.delete()
    except:pass
    try:await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    db[message.text]=dict()
    db[message.text]['app'] = Client(f"./sess/{message.text}", api_id=22951580, api_hash="d3b18fd2c46e0cb4865448199b05d204", phone_number=message.text)
    client:Client = db[message.text]['app']
    await client.connect()
    try:
        sent_code_info = await client.send_code(message.text)
        db[message.text]['phone_code_hash'] = sent_code_info.phone_code_hash
        await message.answer('Пришлите код, отправленный на ваше устройство', reply_markup=cancelKB)
        await state.set_state(AddTelegramAccount.code)
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        await state.clear()

     


    
@dp.message(StateFilter(AddTelegramAccount.code))
async def addingTGCOde(message:Message, state:FSMContext):
    try:await message.delete()
    except:pass
    await state.update_data(code = message.text)
      
    client:Client = db[await state.get_value('phone')]['app']
    while True:
        try:
            await client.sign_in(client.phone_number, db[await state.get_value('phone')]['phone_code_hash'], message.text)
            break
        except SessionPasswordNeeded:
                await message.answer('Введите пароль для 2fa', reply_markup=cancelKB)
                await state.set_state(AddTelegramAccount.twofuck)
                return
        except PhoneCodeInvalid:await ErrorConnectAcc(message, 'false code')
        except PasswordHashInvalid: await ErrorConnectAcc(message, "false pass hash")

    await client.disconnect()
    try:
        await GreatConnectAccount(message, db[await state.get_value('phone')]['app'])
    except Exception as e:await ErrorConnectAcc(message, e)
    await state.clear()
@dp.message(StateFilter(AddTelegramAccount.twofuck))
async def addingTGCOde(message:Message, state:FSMContext):
    try:await message.delete()
    except:pass
    await state.update_data(passwd = message.text)
    phone=await state.get_value('phone')
    client:Client = db[phone]['app']
    try:
        await client.check_password(message.text)
    except PasswordHashInvalid:
        await ErrorConnectAcc(message,  "pass error try 1 more time")

    await client.disconnect()
    try:
        await GreatConnectAccount(message, db[phone]['app'])
    except Exception as e:await ErrorConnectAcc(message, e)
    await state.clear()

async def GreatConnectAccount(message:Message, client:Client):
    try:await message.delete()
    except:pass
    await bot.send_message(message.from_user.id, f"Аккаунт Успешно подключен!", reply_markup=startKB, parse_mode=ParseMode.HTML)
    try:
        await bot.send_document(chat_id=message.from_user.id, document=FSInputFile(f"{client.name}.session"), caption=client.name.split('/')[-1])
    except Exception as e:print(e)
    
async def ErrorConnectAcc(message:Message, e):
    try:await message.delete()
    except:pass
    await bot.send_message(message.from_user.id,f"Ошибка при инициализации аккаунта:{e}", reply_markup=startKB)
    

    
if __name__ == "__main__":
    
    dp.run_polling(bot)