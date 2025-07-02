import pandas as pd
import csv

def normalize_description(text):
    return str(text).strip().lower().replace('  ', ' ')

def detect_separator(path, encoding='latin1'):
    with open(path, 'r', encoding=encoding) as f:
        sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter

def process_sales() -> str:
    input_path = "data/sales.csv"
    output_path = "output/processed_sales.csv"

    sep = detect_separator(input_path)
    df = pd.read_csv(input_path, encoding='latin1', sep=sep)

    col_fecha = next((c for c in df.columns if 'fecha' in c.lower()), None)
    col_desc = next((c for c in df.columns if 'descrip' in c.lower()), None)

    if not col_fecha or not col_desc:
        raise Exception("Missing valid date or description column.")

    df[col_desc] = df[col_desc].apply(normalize_description)
    df['normalized_description'] = df[col_desc]

    df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')

    for col in ['Piezas', 'Precio', 'Costo']:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")
        df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['ingreso'] = df['Piezas'] * df['Precio']
    df['costo'] = df['Piezas'] * df['Costo']
    df['margen'] = df['ingreso'] - df['costo']

    resumen = df.groupby('normalized_description').agg(
        total_units_sold=('Piezas', 'sum'),
        total_income=('ingreso', 'sum'),
        total_cost=('costo', 'sum'),
        total_margin=('margen', 'sum'),
        avg_ticket_price=('Precio', 'mean'),
        sale_frequency_days=(col_fecha, lambda x: x.dt.date.nunique())
    ).reset_index()

    resumen.to_csv(output_path, index=False, encoding='utf-8')
    return output_path
