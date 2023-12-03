import pandas as pd
import numpy as np

import loadData as ld


def calculate_portfolio_performance(data):
    # Obtener el rango de fechas
    start_date = min(pd.to_datetime(data['Date'], format='%d/%m/%Y')) - pd.DateOffset(1)
    end_date = pd.to_datetime('today')

    # Crear un DataFrame con el rango de fechas
    date_range = pd.date_range(start_date, end_date, freq='D')
    performance_df = pd.DataFrame(index=date_range)

    # Inicializar una columna para el rendimiento acumulado

    # performance_df['Cumulative Performance (%)'] = 0.0

    cum_perf= np.zeros(date_range.size)

    # print(performance_df['Cumulative Performance (%)'])

    # Iterar sobre las filas de la tabla de movimientos
    for index, row in data.iterrows():
        ticker = row['Ticker']
        buy_date = pd.to_datetime(row['Date'], format='%d/%m/%Y')
        buy_price = row['StockPrice']

        # print(buy_price)

        # Calcular el cambio porcentual desde la fecha de compra
        price_data = ld.get_historical_data_for_date(ticker, buy_date)['Close']
        # print(price_data)
        t_perf = ((price_data - buy_price) / buy_price) * 100
        # print(t_perf)
        
        cum_perf[-t_perf.size:] += t_perf

    # Actualizar la columna de rendimiento acumulado
    performance_df['Cumulative Performance (%)']=cum_perf
    # print(performance_df['Cumulative Performance (%)'])

    return performance_df

def calculate_stock_contribution(data):
    data=pd.DataFrame(data)
    contribution_data = []

    for index, row in data.iterrows():
        ticker = row['Ticker']
        date = row['Date']
        shares = row['Shares']

        # Obtener datos históricos para el ticker y la fecha seleccionados
        stock_data = ld.get_historical_data_for_date(ticker,date)

    
        buy_price = stock_data.iloc[0]['Close']
        current_price = stock_data.iloc[-1]['Close']

        # Calcular la contribución del stock y agregarla a la lista
        contribution = shares * (current_price - buy_price)
        contribution_data.append({'Ticker': ticker, 'Contribution': contribution})

    # Convertir la lista de diccionarios en un DataFrame
    contribution_df = pd.DataFrame(contribution_data)

    return contribution_df

