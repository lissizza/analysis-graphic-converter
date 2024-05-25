import pytest
from pdf_processing import extract_data_from_page, extract_data_from_all_pages
import pdfplumber


# Пример текста страницы для тестирования
sample_text = """
(врач): Доктор Айболит Метод: Анализ крови
Молочная кислота (лактат, E270) 5.1160 ммоль/моль креат. 4.5000 - 9.0000
"""

def test_extract_data_from_page():
    data, analysis_name = extract_data_from_page(sample_text)
    assert analysis_name == 'Доктор Айболит'
    assert len(data) == 1
    assert data[0] == ('Молочная кислота (лактат, E270)', 5.1160, 4.5000, 9.0000, 'ммоль/моль креат.')


def test_extract_data_from_all_pages(mocker):
    pdf = mocker.MagicMock()
    page = mocker.MagicMock()
    page.extract_text.return_value = sample_text
    pdf.pages = [page]

    data, analysis_name = extract_data_from_all_pages(pdf)
    assert analysis_name == 'Доктор Айболит'
    assert len(data) == 1
    assert data[0] == ('Молочная кислота (лактат, E270)', 5.1160, 4.5000, 9.0000, 'ммоль/моль креат.')
