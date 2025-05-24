import logging
import ssl
import sys
from os import getenv

from aiohttp import web

from aiogram import Dispatcher, Bot, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from core.ocr import OCR

TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
WEBSERVER_HOST = "127.0.0.1"
WEBSERVER_PORT = 8080
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = getenv("BASE_WEBHOOK_URL")
WEBHOOK_SSL_PRIV = getenv("WEBHOOK_SSL_PRIV")
WEBHOOK_SSL_CERT = getenv("WEBHOOK_SSL_CERT")

dp = Dispatcher()
router = Router()
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

@router.message(CommandStart())
async def commandStartHandler(message: Message) -> None:
  await message.answer(f"Hello, {message.from_user.full_name}")

@router.message(F.document)
async def typeFileHandler(message: Message) -> None:

  file = message.document
  source = await bot.download(file)
  detection = OCR(source.read()).detect()
  await message.answer(f"{detection}")

@router.message(F.photo)
async def typePhotoHandler(message: Message) -> None:
  source = await bot.download(message.photo[-1])
  detection = OCR(source.read()).detect()
  await message.answer(f"{detection}")


async def onStartup(bot: Bot) -> None:
  await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", certificate=FSInputFile(WEBHOOK_SSL_CERT), secret_token=WEBHOOK_SECRET,)


async def main() -> None:
  dp.include_router(router)
  dp.startup.register(onStartup)
  app = web.Application()
  webhookRequestsHandler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET,)
  webhookRequestsHandler.register(app, path=WEBHOOK_PATH)
  setup_application(app, dp, bot=bot)
  context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
  context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
  web.run_app(app, host=WEBSERVER_HOST, port=WEBSERVER_PORT, ssl_context=context)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, stream=sys.stdout)
  main()