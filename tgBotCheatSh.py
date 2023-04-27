import logging
import requests
import math
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import Text, Regexp
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import re

API_TOKEN = ''

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)
max_telegram_symbols = 4096 #For divide big message

#Keyboard
kb = [
        [types.KeyboardButton(text="Help me with cli! Please")]
    ]

keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# States
class states(StatesGroup):
    RequestHelp = State()  
    InputNameCli = State()
    Response = State()

async def on_startup():
    await message.answer("/start")
    await message.reply("What's your tools cheatsheet?",reply_markup=keyboard)
    await states.InputNameCli.set()

@dp.message_handler(commands='start')
async def request_start(message: types.Message):

    # Set state
    await states.InputNameCli.set()

@dp.message_handler(lambda message: message.text == "Help me with cli! Please")
async def request_start(message: types.Message):

    # Set state
    await message.reply("What's your tools cheatsheet?",reply_markup=keyboard)
    await states.InputNameCli.set()

@dp.message_handler(Regexp('.*'))
async def request_start(message: types.Message):

    """
    Conversation's entry point
    """
    # Set state
    await message.reply("What's your tools cheatsheet?",reply_markup=keyboard)
    await states.InputNameCli.set()


@dp.message_handler(state=states.InputNameCli)
async def process_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['tool'] = message.text

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]') 

    ResponseDataTool = requests.get('http://cheat.sh/' + str(data['tool']))
    clean_text = ansi_escape.sub('', ResponseDataTool.text)
    
    len_text = len(clean_text)
    print('lenght text:', len(clean_text))

    symbols_msg = len_text / max_telegram_symbols  
    print('part message',symbols_msg)

    amount_send_posts = math.ceil(symbols_msg)
    print('round to bigger (amount messages)', amount_send_posts)

    for offset_msg in range(amount_send_posts):
        await message.answer(clean_text[offset_msg * max_telegram_symbols:max_telegram_symbols + offset_msg * max_telegram_symbols:],reply_markup=keyboard)
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)