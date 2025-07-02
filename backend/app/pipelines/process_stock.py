import pandas as pd
import csv

def normalize_description(text):
    return str(text).strip().lower().replace('  ', ' ')

def detect_separator(path, encoding='latin1'):
    with open(path, 'r', encoding=encoding) as f:
        sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter

def process_stock(daily_demand: int = 5, low_stock_threshold: int = 15) -> str:
    input_path = "data/stock.csv"
    output_path = "output/processed_stock.csv"

    sep = detect_separator(input_path)
    df = pd.read_csv(input_path, encoding='latin1', sep=sep)
    df.columns = df.columns.str.strip()

    col_desc = next((c for c in df.columns if 'descrip' in c.lower()), None)
    if not col_desc:
        raise Exception("Description column not found.")

    df[col_desc] = df[col_desc].apply(normalize_description)
    df['normalized_description'] = df[col_desc]

    if 'Existencias' not in df.columns:
        raise Exception("Missing 'Existencias' column.")

    df['Existencias'] = (
        df['Existencias']
        .astype(str)
        .str.replace(',', '')
        .str.replace(' ', '')
    )
    df['Existencias'] = pd.to_numeric(df['Existencias'], errors='coerce')

    df['coverage_days'] = df['Existencias'] / daily_demand
    df['low_stock_flag'] = (df['coverage_days'] < low_stock_threshold).astype(int)
    df['stock_rotation'] = None  # Placeholder

    resumen = df[['normalized_description', 'Existencias', 'coverage_days', 'low_stock_flag', 'stock_rotation']]
    resumen.to_csv(output_path, index=False, encoding='utf-8')

    return output_path
