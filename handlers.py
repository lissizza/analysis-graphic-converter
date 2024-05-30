import datetime
import logging
import os

import pdfplumber
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TimedOut
from telegram.ext import CallbackContext

from pdf_processing import create_dataframe, extract_data_from_all_pages
from plotting import plot_scales_with_adjusted_ref_labels_spacing

MAX_FILE_SIZE_MB = 10

# Ensure base directories exist
os.makedirs("files", exist_ok=True)


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Команда /start вызвана")
    keyboard = [[InlineKeyboardButton("Helix", callback_data="lab_helix")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите лабораторию:", reply_markup=reply_markup)


async def handle_lab_selection(update: Update, context: CallbackContext) -> None:
    logging.info("Лаборатория Helix выбрана")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Пожалуйста, отправьте PDF файл с результатами анализов."
    )


def save_file(
    user_name: str,
    file_content: bytes,
    extension: str,
    folder_type: str,
    current_time: str,
) -> str:
    # Create user folder
    user_folder = os.path.join("files", user_name)
    os.makedirs(user_folder, exist_ok=True)

    # Create folder for upload or output
    folder_path = os.path.join(user_folder, folder_type)
    os.makedirs(folder_path, exist_ok=True)

    # Create time-stamped subfolder
    time_folder = os.path.join(folder_path, current_time)
    os.makedirs(time_folder, exist_ok=True)

    # Save file
    file_name = f"{current_time}.{extension}"
    file_path = os.path.join(time_folder, file_name)
    with open(file_path, "wb") as f:
        f.write(file_content)

    logging.info(f"File saved to {file_path}")
    return file_path


async def handle_file(update: Update, context: CallbackContext) -> None:
    logging.info("PDF файл получен")
    document = update.message.document

    # Check file size
    if document.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            "Размер файла превышает допустимый лимит в 10 МБ."
        )
        return

    try:
        file = await document.get_file()
    except TimedOut:
        logging.error("Получение файла завершилось по таймауту.")
        await update.message.reply_text(
            "Получение файла завершилось по таймауту. Пожалуйста, попробуйте снова."
        )
        return
    except Exception as e:
        logging.error("An error occurred while getting the file.", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при получении файла: {str(e)}"
        )
        return

    await update.message.reply_text("Идет обработка данных, пожалуйста, подождите...")

    user_name = update.message.from_user.username or update.message.from_user.full_name
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_content = await file.download_as_bytearray()
    upload_path = save_file(user_name, file_content, "pdf", "upload", current_time)

    try:
        with pdfplumber.open(upload_path) as pdf:
            all_data, analysis_name = extract_data_from_all_pages(pdf)

        df_all = create_dataframe(all_data)
        logging.info(f"DataFrame created: {df_all.to_string()}")

        if df_all.empty:
            logging.error("Нет данных в PDF файле")
            await update.message.reply_text("Нет данных в PDF файле.")
            return

        output_png_path = save_file(user_name, b"", "png", "output", current_time)
        output_pdf_path = save_file(user_name, b"", "pdf", "output", current_time)
        plot_scales_with_adjusted_ref_labels_spacing(
            df_all,
            analysis_name,
            save_path_png=output_png_path,
            save_path_pdf=output_pdf_path,
        )

        logging.info(f"Файлы сохранены как {output_png_path} и {output_pdf_path}")

        keyboard = [
            [
                InlineKeyboardButton(
                    "Скачать PNG",
                    callback_data=f"download_png_{user_name}_{current_time}",
                )
            ],
            [
                InlineKeyboardButton(
                    "Скачать PDF",
                    callback_data=f"download_pdf_{user_name}_{current_time}",
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите формат для скачивания:", reply_markup=reply_markup
        )
    except Exception as e:
        logging.error("An error occurred while processing the file.", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при обработке файла: {str(e)}"
        )


async def handle_download(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    action = data[1]
    user_name = data[2]
    timestamp = "_".join(data[3:])
    logging.info(f"Действие {action}, user_name {user_name}, timestamp {timestamp}")

    folder_path = os.path.join("files", user_name, "output", timestamp)

    try:
        if action == "png":
            file_path = os.path.join(folder_path, f"{timestamp}.png")
            logging.info(f"{file_path} запрошен")
            await context.bot.send_document(
                chat_id=query.message.chat_id, document=open(file_path, "rb")
            )
        elif action == "pdf":
            file_path = os.path.join(folder_path, f"{timestamp}.pdf")
            logging.info(f"{file_path} запрошен")
            await context.bot.send_document(
                chat_id=query.message.chat_id, document=open(file_path, "rb")
            )
        await query.message.reply_text(
            "Вы можете загрузить следующий файл для обработки."
        )
    except FileNotFoundError:
        logging.error(f"File {file_path} not found", exc_info=True)
        await query.message.reply_text(f"Файл {file_path} не найден.")
    except Exception as e:
        logging.error("An error occurred while sending the document.", exc_info=True)
        await query.message.reply_text(
            f"Произошла ошибка при отправке документа: {str(e)}"
        )


async def handle_non_pdf(update: Update, context: CallbackContext) -> None:
    logging.info("Получен файл не в формате PDF")
    await update.message.reply_text("Принимаются только файлы в формате PDF.")
