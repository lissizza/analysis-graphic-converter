import pytest
from telegram import Update, User, Message, Document
from telegram.ext import CallbackContext
from handlers import start, handle_lab_selection, handle_file, handle_non_pdf

@pytest.fixture
def mock_update():
    user = User(id=1, first_name='Test', is_bot=False)
    message = Message(message_id=1, date=None, chat=None, from_user=user, text='/start')
    update = Update(update_id=1, message=message)
    return update

@pytest.fixture
def mock_context():
    return CallbackContext(dispatcher=None)

def test_start(mock_update, mock_context):
    result = start(mock_update, mock_context)
    assert result is not None

def test_handle_lab_selection(mock_update, mock_context, mocker):
    update = mock_update
    update.callback_query = mocker.MagicMock()
    update.callback_query.data = 'lab_helix'
    result = handle_lab_selection(update, mock_context)
    assert result is not None

def test_handle_non_pdf(mock_update, mock_context, mocker):
    update = mock_update
    document = mocker.MagicMock(spec=Document)
    document.mime_type = 'image/png'
    update.message.document = document
    result = handle_non_pdf(update, mock_context)
    assert result is not None

def test_handle_file(mock_update, mock_context, mocker):
    update = mock_update
    document = mocker.MagicMock(spec=Document)
    document.mime_type = 'application/pdf'
    update.message.document = document

    mocker.patch('handlers.pdfplumber.open', return_value=mocker.MagicMock())
    result = handle_file(update, mock_context)
    assert result is not None
