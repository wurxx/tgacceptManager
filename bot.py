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
import aiohttp
import random
from config import *

bot = Bot(token='8108403609:AAH-m3yNef-pQBiueT3QlzP6jNBpbc3Dpuc', default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())



class AddTelegramAccount(StatesGroup):
    phone = State()
    code = State()
    twofuck = State()
    channelID = State()

class UpdateChannel(StatesGroup):
    phone= State()
    newID = State()

class IntervalNew(StatesGroup):
    phone = State()
    newInterval = State()

class AddText(StatesGroup):
    phone = State()
    notif = State()

db = {}

async def startmesg():
    return '...'    
    # async with aiohttp.ClientSession() as s:
    #         async with s.get(f"http://{HOST}/interval") as r:
    #             if r.status != 200:print("Ошибка при запросе, интервал отсутствует")
    #             print(await r.json())
    #             interval = [int(x) for x in ''.join((await r.json())[0]).split("-")]
          
    # m = f"Текущий интервал: <code>{min(interval)} - {max(interval)}</code>"
    # return m

async def getAccText(message, phone):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"http://{HOST}/Accs") as r:
            if r.status != 200:
                await message.edit_text( "Ошибка при запросе, интервал отсутствует", reply_markup=startKB)
            acc = [x for x in await r.json() if x[2]==phone]
        async with s.get(f"http://{HOST}/interval?phone={phone}") as r:
            if r.status != 200:
                await message.edit_text( "Ошибка при запросе, интервал отсутствует", reply_markup=startKB)
            print(await r.json())
            interval = [int(x) for x in ''.join((await r.json())[0][0]).split("-")]
            
        return f"☎️:{phone}\nТекущий интервал: <code>{min(interval)} - {max(interval)}</code>\nКанал:<code>{acc[0][-1]}</code>"

@dp.message(CommandStart())
async def startmsg(message:Message):
    if message.from_user.id not in admins:return
    await message.answer(text=await startmesg(), reply_markup=startKB)

@dp.callback_query(F.data == 'cancel')
async def goHome(callback:CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.answer()
    try:await callback.message.delete()
    except:pass
    await bot.send_message(callback.from_user.id,await startmesg(), reply_markup=startKB)


@dp.callback_query(F.data == 'addTgacc', StateFilter(default_state))
async def startAddTgAcc(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text('Введите номер в формате 7900*******', reply_markup=cancelKB)
    await state.set_state(AddTelegramAccount.phone)
    
@dp.message(StateFilter(AddTelegramAccount.phone))
async def addingTGphone(message:Message, state:FSMContext):
    await state.update_data(phone = message.text)
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    try:await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    db[message.text]=dict()
    db[message.text]['app'] = Client(f"./sess/{message.text}", api_id=apiid, api_hash=apihash, phone_number=message.text)
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
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.update_data(code = message.text)
    phone = (await state.get_data())['phone']
    client:Client = db[phone]['app']
    while True:
        try:
            await client.sign_in(client.phone_number, db[phone]['phone_code_hash'], message.text)
            break
        except SessionPasswordNeeded:
                await message.answer('Введите пароль для 2fa', reply_markup=cancelKB)
                await state.set_state(AddTelegramAccount.twofuck)
                return
        except PhoneCodeInvalid:await ErrorConnectAcc(message, 'false code')
        except PasswordHashInvalid: await ErrorConnectAcc(message, "false pass hash")

    await client.disconnect()
    await message.answer('Введите ID канала', reply_markup=cancelKB)
    await state.set_state(AddTelegramAccount.channelID)
    # try:
    #     await GreatConnectAccount(message, db[phone]['app'])
    # except Exception as e:await ErrorConnectAcc(message, e)

@dp.message(StateFilter(AddTelegramAccount.twofuck))
async def addingTGCOde(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.update_data(passwd = message.text)
    phone = (await state.get_data())['phone']
    client:Client = db[phone]['app']
    try:
        await client.check_password(message.text)
    except PasswordHashInvalid:
        await ErrorConnectAcc(message,  "pass error try 1 more time")

    await client.disconnect()
    await message.answer('Введите ID канала', reply_markup=cancelKB)
    await state.set_state(AddTelegramAccount.channelID)




# async def GreatConnectAccount(message:Message, client:Client, state:FSMContext=StateFilter(default_state)):
#     await state.set_state(getChannelID.channelID)
#     await state.set_data({'client':client})
#     await message.edit_text("Введите ID телеграм канала\nПример: -1032884383")
    
    


@dp.message(StateFilter(AddTelegramAccount.channelID))
async def endingConnection(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    data = (await state.get_data())
    print(data)
    client:Client = db[data['phone']]['app']
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.post(f"http://{HOST}/addAcc?phone={client.phone_number}&api_id={client.api_id}&api_hash={client.api_hash}&twofa={client.password}&channelID={message.text}&defaultInterval=30-60") as r:
            print(await r.json())
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await bot.send_message(message.from_user.id, f"Аккаунт Успешно подключен!", reply_markup=startKB, parse_mode=ParseMode.HTML)
    try:
        await bot.send_document(chat_id=message.from_user.id, document=FSInputFile(f"{client.name}.session"), caption=client.name.split('/')[-1])
    except Exception as e:print(e)
    

async def ErrorConnectAcc(message:Message, e):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await bot.send_message(message.from_user.id,f"Ошибка при инициализации аккаунта:{e}", reply_markup=startKB)
    


@dp.callback_query(F.data == 'MyTgacc')
async def myAccs(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"http://{HOST}/Accs") as r:
            if r.status != 200:await callback.answer('Ошибка при отправке запроса')
            myAccs = await r.json()
    inlinekb = []
    if len(myAccs)>0:
        for acc in myAccs:inlinekb+=[[InlineKeyboardButton(text=acc[2], callback_data=f'goAcc_{acc[2]}')]]
        inlinekb+=[[InlineKeyboardButton(text='выход', callback_data='cancel')]]
        print(inlinekb)
        await callback.message.edit_text(text= callback.message.text,reply_markup=InlineKeyboardMarkup(inline_keyboard=inlinekb))
    else:await callback.answer('Пусто 👀')

@dp.callback_query(F.data.startswith('goAcc'))
async def getAcc(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"http://{HOST}/Accs") as r:
            if r.status != 200:await callback.answer('Ошибка при отправке запроса')
            myAccs = await r.json()
    accData = [x for x in myAccs if x[2]==callback.data.split('_')[-1]][0]
    try:
        async with Client(f"./sess/{accData[2]}", accData[0], accData[1], phone_number=accData[2], password=accData[3]) as c:
            lastTgmsg = ''.join([m for m in [x async for x in c.get_chat_history(777000, 1)][0].text.split() if m[:-1].isdigit() and len(m)==6])
            if lastTgmsg != '':await callback.answer(f"Telegram Code: {lastTgmsg}")
            else: await callback.answer('💚') 
        kb = [[InlineKeyboardButton(text="Изменить интервал", callback_data=f"updateInterval_{accData[2]}")],
                [InlineKeyboardButton(text="Текста", callback_data=f"myTexts_{accData[2]}")],
                [InlineKeyboardButton(text="Изменить канал", callback_data=f"changeChannel_{accData[2]}")],
                [InlineKeyboardButton(text='Выход', callback_data=f'cancel')]
                ]
        

        await callback.message.edit_text(await getAccText(callback.message, accData[2]), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    except Exception as e:
        kb = InlineKeyboardMarkup(inline_keyboard=
                                  [[InlineKeyboardButton(text='Удалить', callback_data=f'delAccount_{accData[2]}')], 
                                    [InlineKeyboardButton(text='Выход', callback_data=f'cancel')]]
                                  )
        await callback.message.edit_text(str(e), reply_markup=kb)
        
        
@dp.callback_query(F.data.startswith('delAccount'))
async def delAcc(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
        async with s.post(f"http://{HOST}/delAcc?phone={callback.data.split('_')[-1]}") as r:
            if r.status != 200:await callback.answer('Ошибка при отправке запроса')
            if (await r.json()):await callback.answer();await callback.message.edit_text('Аккаунт удален', reply_markup=startKB)
            

@dp.callback_query(F.data.startswith('updateInterval'))
async def updateInter(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.set_data({"phone":callback.data.split('_')[-1]})
    await callback.message.edit_text("Введите новый интервал проверки новых пользователей в секундах через '-'\nПример: 30-90", reply_markup=cancelKB)
    await state.set_state(IntervalNew.newInterval)
    
@dp.message(StateFilter(IntervalNew.newInterval))
async def gettingIntervalValue(message:Message, state:FSMContext):
    
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    phone = (await state.get_data())['phone']
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.post(f"http://{HOST}/addInter?inter={message.text}&phone={phone}") as r:
            if r.status != 200:await message.edit_text('Ошибка при отправке запроса')
            if await r.json():
                
                await message.answer(await getAccText(message, phone), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить интервал", callback_data=f"updateInterval_{phone}")],
              [InlineKeyboardButton(text="Текста", callback_data=f"myTexts_{phone}")],
              [InlineKeyboardButton(text="Изменить канал", callback_data=f"changeChannel_{phone}")],
                [InlineKeyboardButton(text='Выход', callback_data=f'cancel')]
                ]))
    

@dp.callback_query(F.data.startswith('myTexts'))
async def mainText(callback:CallbackQuery):
    await callback.answer()
    phone = callback.data.split('_')[-1]
    async with aiohttp.ClientSession() as s:
            async with s.get(f"http://{HOST}/texts?phone={phone}") as r:
                if r.status != 200:await callback.answer("Ошибка при запросе, текст отсутствует")
                texts = await r.json()
    kb =[[InlineKeyboardButton(text='Добавить текст', callback_data=f'addTexts_{phone}')]]
    kb += [[InlineKeyboardButton(text=x[0], callback_data=f"goText_{phone}_{x[0]}")] for x in texts]
    
    kb+=[[InlineKeyboardButton(text='выйти', callback_data=f'goAcc_{phone}')]]
    await callback.message.edit_text(text="Выберите текст:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith('goText'))
async def manageText(callback:CallbackQuery):
    await callback.answer()
    txt = callback.data.split('_')[-1]
    phone = callback.data.split('_')[-2]
    kb =[[InlineKeyboardButton(text='Удалить', callback_data=f'removeText_{phone}_{txt}')],
         [InlineKeyboardButton(text='выйти', callback_data=f'goAcc_{phone}')]]
    await callback.message.edit_text(f"Текст: {txt}", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
@dp.callback_query(F.data.startswith('removeText'))
async def dodelTxt(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
            async with s.post(f"http://{HOST}/delText?notif={callback.data.split('_')[-1]}&phone={callback.data.split('_')[-2]}") as r:
                if r.status != 200:await callback.answer("Ошибка при запросе")
    await callback.answer()
    await callback.message.edit_text(await startmesg(), reply_markup=startKB)

@dp.callback_query(F.data.startswith('addTexts'))  
async def addingText1(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.set_state(AddText.notif)
    await state.set_data({"phone":callback.data.split('_')[-1]})
    await callback.message.edit_text('Введите текст...', reply_markup=cancelKB)

@dp.message(StateFilter(AddText.notif))
async def createNewText(message:Message, state:FSMContext):
    phone = (await state.get_data())['phone']
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.post(f"http://{HOST}/addText?notif={message.text}&phone={phone}") as r:
            if r.status != 200:await message.answer("Ошибка при запросе")
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await bot.send_message(message.from_user.id, await getAccText(message, phone), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить интервал", callback_data=f"updateInterval_{phone}")],
              [InlineKeyboardButton(text="Текста", callback_data=f"myTexts_{phone}")],
              [InlineKeyboardButton(text="Изменить канал", callback_data=f"changeChannel_{phone}")],
                [InlineKeyboardButton(text='Выход', callback_data=f'cancel')]
                ]))
                    
@dp.callback_query(F.data.startswith('changeChannel'), StateFilter(default_state))
async def changeChannel(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text('Введите id нового канала', reply_markup=cancelKB)
    await state.set_state(UpdateChannel.newID)
    await state.set_data({'phone':callback.data.split('_')[-1]})

@dp.message(StateFilter(UpdateChannel.newID))
async def saveNewChannel(message:Message, state:FSMContext):
    phone = (await state.get_data())['phone']
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.post(f"http://{HOST}/editChannel?phone={phone}&newChannel={message.text}") as r:
            if r.status != 200 :await message.answer("Ошибка при запросе")
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await bot.send_message(message.from_user.id, await getAccText(message, phone), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить интервал", callback_data=f"updateInterval_{phone}")],
              [InlineKeyboardButton(text="Текста", callback_data=f"myTexts_{phone}")],
              [InlineKeyboardButton(text="Изменить канал", callback_data=f"changeChannel_{phone}")],
                [InlineKeyboardButton(text='Выход', callback_data=f'cancel')]
                ]))
    
    



if __name__ == "__main__":
    
    dp.run_polling(bot)