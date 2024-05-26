import pytest

from pdf_processing import (
    create_dataframe,
    extract_analysis_name,
    extract_data_from_all_pages,
    extract_data_from_page,
)

sample_text = """
(врач): Доктор Айболит Метод: Анализ крови
Молочная кислота (лактат, E270) 5.1160 ммоль/моль креат. 4.5000 - 9.0000
"""

sample_text_no_ref = """
Молочная кислота (лактат, E270) 5.1160 ммоль/моль креат. Референсные значения не
"""

sample_text_ratio = """
Лимонная кислота/Янтарная кислота 1.23 0.9 - 1.5
"""


def test_extract_analysis_name():
    analysis_name = extract_analysis_name(sample_text)
    assert analysis_name == "Доктор Айболит"


def test_extract_data_from_page():
    data = extract_data_from_page(sample_text)
    assert len(data) == 1
    assert data[0] == (
        "Молочная кислота (лактат, E270)",
        5.1160,
        4.5000,
        9.0000,
        "ммоль/моль креат.",
    )


def test_extract_data_from_page_no_ref():
    data = extract_data_from_page(sample_text_no_ref)
    assert len(data) == 1
    assert data[0] == (
        "Молочная кислота (лактат, E270)",
        5.1160,
        None,
        None,
        "ммоль/моль креат.",
    )


def test_extract_data_from_page_ratio():
    data = extract_data_from_page(sample_text_ratio)
    assert len(data) == 1
    assert data[0] == ("Лимонная кислота/Янтарная кислота", 1.23, 0.9, 1.5, "")


@pytest.fixture
def mock_pdf(mocker):
    pdf = mocker.MagicMock()
    page = mocker.MagicMock()
    page.extract_text.return_value = sample_text
    pdf.pages = [page]
    return pdf


def test_extract_data_from_all_pages(mock_pdf):
    data, analysis_name = extract_data_from_all_pages(mock_pdf)
    assert analysis_name == "Доктор Айболит"
    assert len(data) == 1
    assert data[0] == (
        "Молочная кислота (лактат, E270)",
        5.1160,
        4.5000,
        9.0000,
        "ммоль/моль креат.",
    )


def test_create_dataframe():
    data = [
        ("Молочная кислота (лактат, E270)", 5.1160, 4.5000, 9.0000, "ммоль/моль креат.")
    ]
    df = create_dataframe(data)
    assert df.shape == (1, 5)
    assert df["Name"][0] == "Молочная кислота (лактат, E270)"
    assert df["Value"][0] == 5.1160
    assert df["Ref_Min"][0] == 4.5000
    assert df["Ref_Max"][0] == 9.0000
    assert df["Unit"][0] == "ммоль/моль креат."
