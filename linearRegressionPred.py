from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import timedelta

import loadData as ld

import pandas as pd


def train_and_predict_linear_regression(ticker):
    # Obtener datos históricos para el ticker seleccionado
    stock_data = ld.get_historical_data(ticker)

    # Seleccionar columnas relevantes para el modelo (Fecha y Cierre)
    df_lr = stock_data[['Date', 'Close']].copy()

    # Convertir la fecha a un número entero compatible con el modelo
    df_lr['Date'] = pd.to_numeric(df_lr['Date'])

    # Dividir los datos en conjuntos de entrenamiento y prueba
    train, test = train_test_split(df_lr, test_size=0.2, shuffle=False)

    # Preparar los datos de entrenamiento
    X_train = train[['Date']]
    y_train = train['Close']

    # Preparar los datos de prueba
    X_test = test[['Date']]
    y_test = test['Close']

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Realizar predicciones para el conjunto de prueba
    predictions = model.predict(X_test)

    # Agregar nuevas fechas para la predicción (30 días adicionales)
    last_date = df_lr['Date'].max()
    prediction_dates = pd.date_range(start=last_date, periods=31)[1:]

    # Convertir las nuevas fechas a números enteros
    prediction_dates_numeric = pd.to_numeric(prediction_dates)

    # Crear un DataFrame para las fechas de predicción
    df_prediction_dates = pd.DataFrame({'Date': prediction_dates_numeric})

    # Realizar predicciones para las nuevas fechas
    predictions_future = model.predict(df_prediction_dates)

    # Crear un DataFrame para las predicciones futuras
    df_predictions_future = pd.DataFrame({
        'ds': prediction_dates,
        'yhat': predictions_future
    })

    return df_predictions_future