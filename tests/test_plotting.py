import os

import pandas as pd
import pytest

from plotting import plot_scales_with_adjusted_ref_labels_spacing


@pytest.fixture
def sample_dataframe():
    data = {
        "Name": ["Молочная кислота (лактат, E270)"],
        "Value": [5.1160],
        "Ref_Min": [4.5000],
        "Ref_Max": [9.0000],
        "Unit": ["ммоль/моль креат."],
    }
    return pd.DataFrame(data)


def test_plot_scales_with_adjusted_ref_labels_spacing(sample_dataframe):
    df = sample_dataframe
    plot_scales_with_adjusted_ref_labels_spacing(
        df, "Анализ", save_path_png="test.png", save_path_pdf="test.pdf"
    )
    # Дополнительно, можно проверить наличие файлов test.png и test.pdf
    assert os.path.exists("test.png")
    assert os.path.exists("test.pdf")
