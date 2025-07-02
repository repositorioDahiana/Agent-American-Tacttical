import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from mapie.regression import MapieRegressor
from app.pipelines.build_master_dataset import build_master_dataset

def run_model():
    # 🧩 Unir datos procesados desde /output
    df = build_master_dataset()

    # ✅ Definir features y targets
    features = [
        'total_units_sold', 'avg_ticket_price', 'sale_frequency_days',
        'cantidad_total_importada', 'costo_unitario_promedio_import',
        'gastos_logisticos_promedio', 'tiempo_promedio_entrega',
        'Existencias', 'coverage_days'
    ]

    X = df[features]
    y_cantidad = df['cantidad_a_importar']
    y_dias = df['dias_hasta_proxima_importacion']

    # ✂️ Separar datos para entrenamiento y prueba
    X_train, X_test, y_train_cant, y_test_cant = train_test_split(X, y_cantidad, test_size=0.2, random_state=42)
    _, _, y_train_dias, y_test_dias = train_test_split(X, y_dias, test_size=0.2, random_state=42)

    # ⚙️ Entrenar modelo para cantidad a importar
    modelo_cant = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    modelo_cant.fit(X_train, y_train_cant)
    pred = modelo_cant.predict(X_test)

    # 📊 Métricas
    mae = mean_absolute_error(y_test_cant, pred)
    rmse = np.sqrt(mean_squared_error(y_test_cant, pred))

    # 🧠 Conformal Prediction
    mapie = MapieRegressor(estimator=modelo_cant, cv=-1, method="plus")
    mapie.fit(X_train, y_train_cant)
    pred_interval, intervalo = mapie.predict(X_test, alpha=0.1)
    intervalo = intervalo.squeeze()

    # 📈 Guardar gráfico
    os.makedirs("output", exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(y_test_cant.values, label="Real")
    plt.plot(pred_interval, label="Predicción")
    plt.fill_between(range(len(pred_interval)), intervalo[:, 0], intervalo[:, 1], alpha=0.3, label="Intervalo 90%")
    plt.title("Predicción de Cantidad a Importar con Intervalo de Confianza")
    plt.xlabel("Muestras")
    plt.ylabel("Cantidad")
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/prediction_plot.png")
    plt.close()

    # 🔁 Predicción completa
    df['pred_cantidad'] = modelo_cant.predict(X)

    # Entrenar también para días hasta próxima importación
    modelo_dias = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    modelo_dias.fit(X_train, y_train_dias)
    df['pred_dias'] = modelo_dias.predict(X)

    # 📦 Filtrar productos recomendados
    productos = df[df['pred_cantidad'] > 0].copy()
    productos = productos.sort_values(by='pred_dias')

    # 💾 Guardar CSV con resultados
    output_csv = "output/productos_recomendados.csv"
    productos[['normalized_description', 'pred_cantidad', 'pred_dias']].to_csv(output_csv, index=False, encoding='utf-8')

    return {
        "mae": mae,
        "rmse": rmse,
        "csv": output_csv,
        "image": "output/prediction_plot.png"
    }
