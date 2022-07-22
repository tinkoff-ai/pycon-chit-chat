from collections import defaultdict

from aiogram import Bot, Dispatcher, executor, types
from pydantic import BaseSettings


class TelegramSettings(BaseSettings):
    token: str

    class Config:
        env_prefix = 'TG_'


tg_settings = TelegramSettings()

bot = Bot(token=tg_settings.token)
dp = Dispatcher(bot=bot)

USER_CONTEXT = defaultdict(list)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer('Welcome to the bot!')


@dp.message_handler(content_types=['text'])
async def continue_dialog(message: types.Message):
    await message.answer('Wassup')


if __name__ == "__main__":
    executor.start_polling(dp)
