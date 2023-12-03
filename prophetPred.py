from prophet import Prophet
import loadData as ld

from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=24*30)  # Hace 2 años

def train_and_predict(ticker):
    # Obtener datos históricos
    historical_data = ld.get_historical_data_for_date(ticker,'01/01/2020')

    # Preparar los datos para Prophet
    df_prophet = historical_data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

    df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)

    # Inicializar y entrenar el modelo
    model = Prophet()
    model.fit(df_prophet)

    # Crear un DataFrame con las fechas futuras (30 días)
    future = model.make_future_dataframe(periods=30)

    # Hacer predicciones
    forecast = model.predict(future)

    return forecast[['ds', 'yhat']]
