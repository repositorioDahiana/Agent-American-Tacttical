import pandas as pd
import csv

def normalize_description(text):
    return str(text).strip().lower().replace('  ', ' ')

def detect_separator(path, encoding='latin1'):
    with open(path, 'r', encoding=encoding) as f:
        sample = f.read(2048)
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter

def process_imports() -> str:
    input_path = "data/imports.csv"
    output_path = "output/processed_imports.csv"

    sep = detect_separator(input_path)
    df = pd.read_csv(input_path, encoding='latin1', sep=sep)

    col_desc = next((c for c in df.columns if 'descrip' in c.lower()), None)
    if not col_desc:
        raise Exception("No description column found.")
    df[col_desc] = df[col_desc].apply(normalize_description)
    df['normalized_description'] = df[col_desc]

    df['Actual Pickup Date'] = pd.to_datetime(df['Actual Pickup Date'], errors='coerce')
    df['Actual Delivery Date'] = pd.to_datetime(df['Actual Delivery Date'], errors='coerce')
    df['tiempo_entrega'] = (df['Actual Delivery Date'] - df['Actual Pickup Date']).dt.days

    numeric_cols = ['CANTIDAD', 'COSTO UNITARIO EN MEX', 'GASTOS LOGISTICOS MXN']
    for col in numeric_cols:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '')
            .str.replace('.', '', regex=False)
            .str.replace(' ', '')
            .str.replace(',', '.', regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    resumen = df.groupby('normalized_description').agg(
        cantidad_total_importada=('CANTIDAD', 'sum'),
        costo_unitario_promedio_import=('COSTO UNITARIO EN MEX', 'mean'),
        gastos_logisticos_promedio=('GASTOS LOGISTICOS MXN', 'mean'),
        tiempo_promedio_entrega=('tiempo_entrega', 'mean'),
        ultima_fecha_importacion=('Actual Delivery Date', 'max')
    ).reset_index()

    resumen.to_csv(output_path, index=False, encoding='utf-8')
    return output_path
