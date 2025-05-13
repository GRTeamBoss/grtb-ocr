import asyncio
import logging
import sys
from os import getenv

from aiogram import Dispatcher, Bot, md, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from typing import BinaryIO

from core.ocr import OCR

TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")

dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

@dp.message(CommandStart())
async def commandStartHandler(message: Message) -> None:
  await message.answer(f"Hello, {message.from_user.full_name}")

@dp.message(F.document)
async def typeFileHandler(message: Message) -> None:

  file = message.document
  source = await bot.download(file)
  detection = OCR(source.read()).detect()
  await message.answer(f"{detection}")

@dp.message(F.photo)
async def typePhotoHandler(message: Message) -> None:
  source = await bot.download(message.photo[-1])
  detection = OCR(source.read()).detect()
  await message.answer(f"{detection}")

async def main():
  await dp.start_polling(bot)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, stream=sys.stdout)
  asyncio.run(main())