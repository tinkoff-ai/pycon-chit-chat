from collections import defaultdict

from aiogram import Bot, Dispatcher, executor, types

from tg_bot.responder import Responder
from tg_bot.settings import GenerationSettings, ModelSettings, TelegramSettings

generation_settings = GenerationSettings()
model_settings = ModelSettings()
tg_settings = TelegramSettings()

bot = Bot(token=tg_settings.token)
dp = Dispatcher(bot=bot)

USER_HISTORY = defaultdict(list)

model = Responder(
    generator_model_path=model_settings.generator_model_path,
    crossencoder_model_path=model_settings.crossencoder_model_path,
    toxicity_classifier_path=model_settings.toxicity_classifier_model_path,
    max_toxicity_score=model_settings.max_toxicity_score
)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Welcome to the bot!")


@dp.message_handler(commands=['clean_context'])
async def clean_context(message: types.Message):
    USER_HISTORY[message.from_user.id] = []
    await message.answer("Context cleaned")


@dp.message_handler(content_types=['text'])
async def continue_dialog(message: types.Message):
    user_id = message.from_user.id
    USER_HISTORY[user_id].append(message.text)

    dialog = USER_HISTORY[user_id][-3:]
    response = model.respond(dialog, generation_settings)
    if not response:
        USER_HISTORY[user_id].pop()
    else:
        USER_HISTORY[user_id].append(response)
        await message.answer(response)

if __name__ == "__main__":
    executor.start_polling(dp)
