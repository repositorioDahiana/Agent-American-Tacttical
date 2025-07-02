import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
from datetime import datetime
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'output', 'descriptive')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Catálogo de gráficas descriptivas
DESCRIPTIVE_GRAPHS = [
    {
        "id": "trend_imports",
        "name": "Tendencia histórica de importaciones",
        "description": "Muestra la evolución de las importaciones a lo largo del tiempo.",
        "generator": "generate_trend_imports"
    },
    {
        "id": "top_imported_products",
        "name": "Top 5 productos más importados (último trimestre)",
        "description": "Presenta los productos más importados en el último trimestre.",
        "generator": "generate_top_imported_products"
    },
    {
        "id": "logistics_cost_trend",
        "name": "Tendencia del costo logístico",
        "description": "Evolución del costo logístico a lo largo del tiempo.",
        "generator": "generate_logistics_cost_trend"
    },
    {
        "id": "low_rotation_high_margin",
        "name": "Producto con menor rotación y mayor margen",
        "description": "Identifica el producto con menor rotación pero mayor margen de ganancia.",
        "generator": "generate_low_rotation_high_margin"
    },
]

def load_data(filename: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def save_plot_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"

def find_column(df, candidates):
    for col in df.columns:
        if col.lower() in [c.lower() for c in candidates]:
            return col
    raise ValueError(f"No se encontró ninguna de las columnas: {candidates}")

# --- Funciones de generación de gráficas ---
def generate_trend_imports() -> str:
    """Genera la gráfica de tendencia histórica de importaciones."""
    df = load_data('imports.csv')
    fecha_col = find_column(df, ['fecha', 'Fecha', 'FECHA', 'date', 'Date'])
    cantidad_col = find_column(df, ['cantidad', 'Cantidad', 'CANTIDAD'])
    # Adaptar a tus columnas reales
    fecha_col = find_column(df, [fecha_col, 'Date'])
    cantidad_col = find_column(df, [cantidad_col, 'CANTIDAD'])
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    df_group = df.groupby(df[fecha_col].dt.to_period('M'))[cantidad_col].sum().reset_index()
    df_group[fecha_col] = df_group[fecha_col].dt.to_timestamp()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=df_group, x=fecha_col, y=cantidad_col, marker='o', ax=ax)
    ax.set_title('Tendencia histórica de importaciones')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad importada')
    return save_plot_to_base64(fig)

def generate_top_imported_products() -> str:
    """Genera la gráfica de top 5 productos más importados en el último trimestre."""
    df = load_data('imports.csv')
    fecha_col = find_column(df, ['fecha', 'Fecha', 'FECHA', 'date', 'Date'])
    cantidad_col = find_column(df, ['cantidad', 'Cantidad', 'CANTIDAD'])
    producto_col = find_column(df, ['producto', 'Producto', 'PRODUCTO', 'Descripcion producto'])
    # Adaptar a tus columnas reales
    fecha_col = find_column(df, [fecha_col, 'Date'])
    cantidad_col = find_column(df, [cantidad_col, 'CANTIDAD'])
    producto_col = find_column(df, [producto_col, 'Descripcion producto'])
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    last_quarter = df[fecha_col].max() - pd.DateOffset(months=3)
    df_recent = df[df[fecha_col] >= last_quarter]
    top_products = df_recent.groupby(producto_col)[cantidad_col].sum().nlargest(5).reset_index()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(data=top_products, x=cantidad_col, y=producto_col, ax=ax, palette='Blues_d')
    ax.set_title('Top 5 productos más importados (último trimestre)')
    ax.set_xlabel('Cantidad importada')
    ax.set_ylabel('Producto')
    return save_plot_to_base64(fig)

def generate_logistics_cost_trend() -> str:
    """Genera la gráfica de tendencia del costo logístico."""
    df = load_data('imports.csv')
    fecha_col = find_column(df, ['fecha', 'Fecha', 'FECHA', 'date', 'Date'])
    costo_col = find_column(df, ['costo_logistico', 'Costo_logistico', 'CostoLogistico', 'costo', 'Costo', 'GASTOS LOGISTICOS MXN'])
    # Adaptar a tus columnas reales
    fecha_col = find_column(df, [fecha_col, 'Date'])
    costo_col = find_column(df, [costo_col, 'GASTOS LOGISTICOS MXN'])
    df[fecha_col] = pd.to_datetime(df[fecha_col])
    df_group = df.groupby(df[fecha_col].dt.to_period('M'))[costo_col].sum().reset_index()
    df_group[fecha_col] = df_group[fecha_col].dt.to_timestamp()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=df_group, x=fecha_col, y=costo_col, marker='o', ax=ax, color='orange')
    ax.set_title('Tendencia del costo logístico')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Costo logístico')
    return save_plot_to_base64(fig)

def generate_low_rotation_high_margin() -> str:
    """Genera la gráfica del producto con menor rotación y mayor margen."""
    stock = load_data('stock.csv')
    sales = load_data('sales.csv')
    producto_col = find_column(stock, ['producto', 'Producto', 'PRODUCTO', 'Descripcion producto'])
    cantidad_col = find_column(stock, ['cantidad', 'Cantidad', 'CANTIDAD', 'Existencias '])
    # Adaptar a tus columnas reales
    producto_col = find_column(stock, [producto_col, 'Descripcion producto'])
    cantidad_col = find_column(stock, [cantidad_col, 'Existencias '])
    # Suponiendo columnas: 'rotacion', 'margen'
    if 'rotacion' not in stock.columns:
        ventas = sales.groupby(producto_col)['Piezas'].sum()
        stock_prom = stock.groupby(producto_col)[cantidad_col].mean()
        rotacion = (ventas / stock_prom).fillna(0)
        stock['rotacion'] = stock[producto_col].map(rotacion)
    if 'margen' not in stock.columns:
        if 'Precio' in sales.columns and 'Costo promedio ' in stock.columns:
            stock['margen'] = (sales['Precio'].mean() - stock['Costo promedio ']) / stock['Costo promedio ']
        else:
            stock['margen'] = 0
    filtered = stock[[producto_col, 'rotacion', 'margen']].dropna()
    filtered = filtered.sort_values(['rotacion', 'margen'], ascending=[True, False]).head(1)
    fig, ax = plt.subplots(figsize=(6,2))
    sns.barplot(data=filtered, x='margen', y=producto_col, ax=ax, color='green')
    ax.set_title('Producto con menor rotación y mayor margen')
    ax.set_xlabel('Margen')
    ax.set_ylabel('Producto')
    return save_plot_to_base64(fig)

def get_descriptive_graphs_catalog() -> List[Dict]:
    """Devuelve el catálogo de gráficas descriptivas disponibles."""
    return DESCRIPTIVE_GRAPHS

def get_graph_by_id(graph_id: str) -> str:
    """Genera y devuelve la gráfica correspondiente al id."""
    for graph in DESCRIPTIVE_GRAPHS:
        if graph['id'] == graph_id:
            func = globals()[graph['generator']]
            return func()
    raise ValueError(f"Gráfica con id '{graph_id}' no encontrada.") 