# Importar librerías
import dash
from dash import dcc, html
from dash import dash_table
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

# Inicializar la aplicación
app = dash.Dash(__name__)

# Datos iniciales de acciones (puedes agregar más según tus necesidades)
initial_tickers = ['AAPL', 'GOOGL', 'MSFT']
start_date = datetime.now() - timedelta(days=6*30)  # Hace 6 meses
buy_date_example=datetime.now()-timedelta(days=15)
end_date = datetime.now()-timedelta(days=1)
print(start_date)
print(end_date)

# Crear DataFrame de ejemplo (para probar la aplicación)
# df_example = pd.DataFrame({'Ticker': initial_tickers * (len(initial_tickers) * 2),
#                            'Type': ['Buy', 'Sell'] * (len(initial_tickers)),
#                            'Shares': [5, 10, -7, 3, -5] * (len(initial_tickers) // 2),
#                            'Date': pd.date_range(start_date, periods=(len(initial_tickers) * 2)).tolist()})

df_example = pd.DataFrame({'Ticker': initial_tickers,
                           'Type': ['Buy', 'Buy','Buy'] ,
                           'Shares': [5, 10, 6],
                           'Date': [buy_date_example,buy_date_example,buy_date_example]})

# Diseño de la aplicación
app.layout = html.Div([
    # Primera fila
    html.Div([
        # Parte Izquierda (Portfolio Movements)
        html.Div([
            html.H3("Portfolio Movements"),
            # Aquí irá la tabla de movimientos
            # (Por ahora, solo mostraremos el DataFrame de ejemplo)
            dash_table.DataTable(
                id='table_movements',
                columns=[
                    {'name': col, 'id': col, 'editable': True} for col in df_example.columns
                ],
                data=df_example.to_dict('records'),
                editable=True,
            ),
            html.Button("Update Data", id="update_button", n_clicks=0, style={'margin-top': '10px'}),
            
        ], style={'width': '48%', 'display': 'inline-block'}),

        # Parte Derecha (Evolution of my stocks)
        html.Div([
            html.H3("Evolution of my stocks"),
            # Dropdown para seleccionar acciones en el gráfico
            dcc.Checklist(
                id='stock_checklist',
                options=[{'label': ticker, 'value': ticker} for ticker in initial_tickers],
                value=initial_tickers,
                # inline=True
            ),
            # Gráfico de evolución de acciones
            dcc.Graph(id='stock_evolution'),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),

    # Segunda fila
    html.Div([
        html.H3("Performance of my portfolio"),
        # Botones para seleccionar el tipo de gráfico
        dcc.RadioItems(
            id='chart_selector',
            options=[
                {'label': 'by time', 'value': 'by_time'},
                {'label': 'by sector', 'value': 'by_sector'},
                {'label': 'contribution', 'value': 'contribution'}
            ],
            value='by_time',
            labelStyle={'display': 'block'}
        ),
        # Gráfico correspondiente al tipo seleccionado
        dcc.Graph(id='selected_chart'),
    ]),
])

# Callback para actualizar la tabla de movimientos
@app.callback(
    Output('table_movements', 'data'),
    Input('table_movements', 'data_previous'),
    State('table_movements', 'data')
)
def update_table(prev_data, data):
    if prev_data != data:
        # Convertir la lista de diccionarios a un DataFrame
        df = pd.DataFrame(data)
        
        # Validación de datos (compra: 1, venta: -1)
        df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce')
        df['Shares'] *= df['Type'].apply(lambda x: 1 if x.lower() == 'buy' else -1)
        
        # Validación de fechas en formato dd/mm/yyyy
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')

        # Convertir el DataFrame de vuelta a la lista de diccionarios
        updated_data = df.to_dict('records')
        
        return updated_data
    return data

# Callback para actualizar el gráfico de evolución de acciones
@app.callback(
    Output('stock_evolution', 'figure'),
    Input('stock_checklist', 'value'),
    State('table_movements', 'data')
)
def update_stock_evolution(selected_stocks, data):
    if not data or not selected_stocks:
        # Si no hay datos o no hay acciones seleccionadas, no hay nada que mostrar
        return {'data': [], 'layout': {}}

    # Convertir la tabla de movimientos a un DataFrame
    df = pd.DataFrame(data)

    # Crear un DataFrame vacío para almacenar los datos de yfinance
    df_yfinance = pd.DataFrame()

    # Obtener datos históricos para cada ticker seleccionado
    for ticker in selected_stocks:
        stock_data = get_historical_data(ticker, df['Date'].min(), df['Date'].max())

        stock_data['Ticker'] = ticker
        
         # Filtrar las fechas para las cuales hay datos
        stock_data = stock_data[stock_data['Date'].isin(df['Date'])]
        
        df_yfinance = pd.concat([df_yfinance, stock_data])

    # Actualizar la tabla con los precios de cierre de las acciones en la fecha de compra
    df = pd.merge(df, df_yfinance[['Date', 'Ticker', 'Close']], left_on=['Ticker', 'Date'], right_on=['Ticker', 'Date'],
                  how='left', suffixes=('', '_close'))

    # Crear un gráfico de línea
    fig = {
        'data': [
            {'x': df[df['Ticker'] == ticker]['Date'],
             'y': df[df['Ticker'] == ticker]['Close'],
             'name': ticker}
            for ticker in selected_stocks
        ],
        'layout': {
            'title': 'Evolution of my stocks',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Close Price'},
            'legend': {'orientation': 'h'},
        }
    }

    return fig


# Callback para actualizar la gráfica seleccionada
@app.callback(
    Output('selected_chart', 'figure'),
    Input('chart_selector', 'value'),
    State('table_movements', 'data')
)
def update_selected_chart(selected_chart, data):
    if not data:
        return {'data': [], 'layout': {}}

    # Convertir la tabla de movimientos a un DataFrame
    df = pd.DataFrame(data)

    if selected_chart == 'by_time':
        # Gráfico "by time" (rendimiento total)
        fig = {
            'data': [
                {'x': df[df['Ticker'] == ticker]['Date'],
                 'y': df[df['Ticker'] == ticker]['Shares'].cumsum(),
                 'name': ticker}
                for ticker in df['Ticker'].unique()
            ],
            'layout': {
                'title': 'Performance by Time',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Cumulative Shares'},
                'legend': {'orientation': 'h'},
            }
        }
    elif selected_chart == 'by_sector':
        # Gráfico "by sector" (rendimiento por sector)
        # (Este es un gráfico de barras de ejemplo, puedes personalizar según tus necesidades)
        fig = {
            'data': [
                {'x': ['Technology', 'Health', 'Finance'],
                 'y': [100, 150, 80],
                 'type': 'bar',
                 'name': 'Portfolio'}
            ],
            'layout': {
                'title': 'Performance by Sector',
                'xaxis': {'title': 'Sector'},
                'yaxis': {'title': 'Value'},
            }
        }
    elif selected_chart == 'contribution':
        # Gráfico "contribution" (contribución de cada acción)
        # (Este es un gráfico de cascada de ejemplo, puedes personalizar según tus necesidades)
        fig = {
            'data': [
                {'x': df['Ticker'],
                 'y': [10, -5, 8, -3, 12],
                 'type': 'waterfall',
                 'name': 'Contribución'}
            ],
            'layout': {
                'title': 'Contribution of Each Stock',
                'xaxis': {'title': 'Ticker'},
                'yaxis': {'title': 'Contribution'},
            }
        }
    else:
        fig = {'data': [], 'layout': {}}

    return fig

# Función para obtener datos históricos de yfinance
def get_historical_data(ticker, start_date, end_date):
    # Eliminar la información de tiempo de las fechas
    start_date = start_date.split("T")[0]
    end_date = end_date.split("T")[0]

    # Create a Ticker object for the given stock symbol
    stock_ticker = yf.Ticker(ticker)

    # Get historical market data for the specified period
    historical_data = stock_ticker.history(start=start_date, end=end_date)

    # Resetting the index to have 'Date' as a column instead of the index
    historical_data.reset_index(inplace=True)

    return historical_data


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
