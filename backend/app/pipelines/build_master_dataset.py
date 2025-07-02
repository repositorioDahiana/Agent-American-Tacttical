import pandas as pd

def build_master_dataset():
    # Cargar archivos ya procesados
    sales = pd.read_csv('output/processed_sales.csv')
    imports = pd.read_csv('output/processed_imports.csv')
    stock = pd.read_csv('output/processed_stock.csv')

     # Unificar por descripción normalizada
    df = sales.merge(imports, on='normalized_description', how='left') \
              .merge(stock, on='normalized_description', how='left')

    # Demanda diaria estimada (ventas_totales / 90 días)
    df['demanda_diaria_estimada'] = df['total_units_sold'] / 90

    # Rellenar tiempos promedio de entrega si están vacíos
    avg_delivery_time = df['tiempo_promedio_entrega'].mean(skipna=True)
    df['tiempo_promedio_entrega'] = df['tiempo_promedio_entrega'].fillna(avg_delivery_time)

    # Calcular cantidad estimada a importar
    df['cantidad_a_importar'] = df['demanda_diaria_estimada'] * df['tiempo_promedio_entrega']
    df['cantidad_a_importar'] = df['cantidad_a_importar'].fillna(df['total_units_sold'] / 2)

    # Asegurar formato de fecha y llenar valores faltantes
    df['ultima_fecha_importacion'] = pd.to_datetime(df['ultima_fecha_importacion'], errors='coerce')
    df['ultima_fecha_importacion'] = df['ultima_fecha_importacion'].fillna(pd.Timestamp('2024-12-01'))

    # Calcular días desde la última importación
    df['dias_hasta_proxima_importacion'] = (
        pd.Timestamp.today() - df['ultima_fecha_importacion']
    ).dt.days

    # Guardar dataset unificado
    df.to_csv('output/master_dataset.csv', index=False)
    print("✅ Archivo generado: master_dataset.csv con valores completados.")

    return df