import re
from typing import List, Tuple, Union
import pdfplumber
import pandas as pd
import logging

PATTERN_GENERIC = re.compile(r'([A-Za-zА-Яа-яёЁ0-9\-\(\),\s]+)\s+([\d.]+)\s*(нмоль/мл|мкмоль/л|нмоль/л|ммоль/моль креат.|у.е./моль креат.|ммоль/л)?\s*([\d.]+)?\s*-\s*([\d.]+)?')
PATTERN_NO_REF = re.compile(r'([A-Za-zА-Яа-яёЁ0-9\-\(\),\s]+)\s+([\d.]+)\s+(нмоль/мл|мкмоль/л|нмоль/л|ммоль/моль креат.|у.е./моль креат.|ммоль/л)\s+Референсные значения не')
PATTERN_RATIO = re.compile(r'([A-Za-zА-Яа-яёЁ0-9\-\(\),/\s]+)\s+([\d.]+)\s+([\d.]+)\s*-\s*([\d.]+)')


def extract_analysis_name(text: str) -> str:
    if '(врач):' in text and 'Метод:' in text:
        analysis_name_start = text.find('(врач):') + len('(врач):')
        analysis_name_end = text.find('Метод:')
        return text[analysis_name_start:analysis_name_end].strip()
    return ''


def extract_data_from_page(text: str) -> List[Tuple[str, float, Union[float, None], Union[float, None], str]]:
    all_data: List[Tuple[str, float, Union[float, None], Union[float, None], str]] = []
    lines = text.split('\n')

    for line in lines:
        match = PATTERN_GENERIC.match(line)
        if match:
            name, value, unit, ref_min, ref_max = match.groups()
            if ref_min and ref_max:
                all_data.append((name, float(value), float(ref_min), float(ref_max), unit))
            else:
                all_data.append((name, float(value), None, None, unit))
        elif 'не обнаружено' in line:
            parts = line.split('0.00')
            all_data.append((parts[0].strip(), 0.0, 0.0, 0.0, parts[1].split()[0]))
        else:
            match_no_ref = PATTERN_NO_REF.match(line)
            if match_no_ref:
                name, value, unit = match_no_ref.groups()[:3]
                all_data.append((name, float(value), None, None, unit))
            else:
                match_ratio = PATTERN_RATIO.match(line)
                if match_ratio:
                    name, value, ref_min, ref_max = match_ratio.groups()
                    all_data.append((name, float(value), float(ref_min), float(ref_max), ''))

    return all_data


def extract_data_from_all_pages(pdf: pdfplumber.PDF) -> Tuple[List[Tuple[str, float, Union[float, None], Union[float, None], str]], str]:
    all_data: List[Tuple[str, float, Union[float, None], Union[float, None], str]] = []
    analysis_name = ''

    for page in pdf.pages:
        page_text = page.extract_text()
        # logging.info(f'Extracted text from page: {page_text}')
        page_data = extract_data_from_page(page_text)
        all_data.extend(page_data)
        if not analysis_name:
            analysis_name = extract_analysis_name(page_text)
        # logging.info(f'Extracted data from page: {page_data}')

    logging.info(f'Analysis name: {analysis_name}')
    return all_data, analysis_name


def create_dataframe(data: List[Tuple[str, float, Union[float, None], Union[float, None], str]]) -> pd.DataFrame:
    df = pd.DataFrame(data, columns=['Name', 'Value', 'Ref_Min', 'Ref_Max', 'Unit'])
    df['Value'] = df['Value'].replace({'не': None}).astype(float)
    df['Ref_Min'] = pd.to_numeric(df['Ref_Min'], errors='coerce')
    df['Ref_Max'] = pd.to_numeric(df['Ref_Max'], errors='coerce')
    return df
