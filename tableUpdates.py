import loadData as ld

import pandas as pd

def add_stock_price_to_table(data):
    # Convertir la lista de diccionarios a un DataFrame
    df = pd.DataFrame(data)
    
    # Validación de fechas en formato dd/mm/yyyy
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')

    # Iterar sobre las filas del DataFrame para obtener el precio de las acciones
    for index, row in df.iterrows():
        ticker = row['Ticker']
        date = row['Date']

        # Obtener datos históricos para el ticker
        df_ticker=ld.get_historical_data(ticker)
        
        
        # Cambiar el formato de la columna 'Date'
        df_ticker['Date'] = pd.to_datetime(df_ticker['Date']).dt.strftime('%d/%m/%Y')
        # print(df_ticker['Date'])

        stock_data = df_ticker[df_ticker['Date'] == date]
        

       # Verificar si hay datos para la fecha específica
        if not stock_data.empty:
            # Obtener el precio de cierre para esa fecha
            stock_price = stock_data.iloc[0]['Close']
            # print(stock_price)
            # Asignar el precio de las acciones a la celda correspondiente en el DataFrame original
            df.at[index, 'StockPrice'] = stock_price
        else:
            # Si no hay datos para la fecha específica, puedes manejarlo como desees
            print(f"No hay datos para el ticker {ticker} en la fecha {date}")

    # Convertir el DataFrame de vuelta a la lista de diccionarios
    updated_data = df
    # print(updated_data)

    return updated_data