import asyncio
import logging
import os
import signal

import nest_asyncio
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers import (
    handle_download,
    handle_file,
    handle_lab_selection,
    handle_non_pdf,
    start,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Patch existing event loop
nest_asyncio.apply()


async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(handle_lab_selection, pattern="^lab_helix$")
    )
    application.add_handler(
        MessageHandler(filters.Document.MimeType("application/pdf"), handle_file)
    )
    application.add_handler(MessageHandler(~filters.Document.PDF, handle_non_pdf))
    application.add_handler(
        CallbackQueryHandler(handle_download, pattern="^download_(png|pdf)_")
    )

    logging.info("Bot started and ready to receive commands")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler(sig):
        logging.info(f"Received exit signal {sig.name}...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler, sig)

    await stop_event.wait()

    logging.info("Stopping application...")
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    logging.info("Application stopped gracefully")


if __name__ == "__main__":
    asyncio.run(main())
