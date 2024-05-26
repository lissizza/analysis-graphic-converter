import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import CallbackQuery, Document, Message, Update, User
from telegram.ext import CallbackContext

from handlers import (
    handle_download,
    handle_file,
    handle_lab_selection,
    handle_non_pdf,
    save_file,
    start,
)


@pytest.fixture
def update():
    message = MagicMock(spec=Message)
    user = User(id=1, is_bot=False, first_name="Test")
    message.from_user = user
    message.document = None
    message.reply_text = AsyncMock()
    callback_query = MagicMock(spec=CallbackQuery)
    callback_query.message = message
    callback_query.answer = AsyncMock()
    callback_query.edit_message_text = AsyncMock()
    update = MagicMock(spec=Update)
    update.message = message
    update.callback_query = callback_query
    return update


@pytest.fixture
def context():
    context = MagicMock(spec=CallbackContext)
    context.bot = MagicMock()
    return context


def test_start(update, context):
    asyncio.run(start(update, context))
    update.message.reply_text.assert_called_once()


def test_handle_lab_selection(update, context):
    update.callback_query = update.callback_query
    asyncio.run(handle_lab_selection(update, context))
    update.callback_query.edit_message_text.assert_called_once()


def test_handle_non_pdf(update, context):
    asyncio.run(handle_non_pdf(update, context))
    update.message.reply_text.assert_called_once()


def test_save_file():
    user_name = "test_user"
    file_content = b"test_content"
    extension = "pdf"
    folder_type = "upload"
    current_time = "2024-01-01_12-00-00"

    file_path = save_file(user_name, file_content, extension, folder_type, current_time)

    assert os.path.exists(file_path)


def test_handle_file(update, context):
    document = Document(
        file_id="1234",
        file_unique_id="unique1234",
        file_size=1000,
        file_name="test.pdf",
        mime_type="application/pdf",
    )
    update.message.document = document
    asyncio.run(handle_file(update, context))
    update.message.reply_text.assert_called_once()


def test_handle_download(update, context):
    query = update.callback_query
    query.data = "download_pdf_test_user_2024-01-01_12-00-00"
    query.message.chat_id = 12345

    with patch("handlers.os.path.exists", return_value=True):
        with patch("builtins.open", new_callable=MagicMock):
            asyncio.run(handle_download(update, context))
            query.answer.assert_called_once()
            context.bot.send_document.assert_called_once()
            query.message.reply_text.assert_called_once()
