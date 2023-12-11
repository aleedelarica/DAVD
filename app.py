# Importar librerías
import dash
from dash import dcc, html
from dash import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime
import dataCalculation as sp
import loadData as ld
import tableUpdates as tu
import prophetPred as p
import linearRegressionPred as lr

# Inicializar la aplicación
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.PULSE])

# Carga el archivo xlsx
file_path = 'movements.xlsx'
df_movements = pd.read_excel(file_path)

df_movements['Date']=df_movements['Date'].dt.strftime('%d/%m/%Y')

df_movements=tu.add_stock_price_to_table(df_movements)

tickers=df_movements['Ticker'].unique()

# df_movements = pd.DataFrame({'Ticker': tickers,
#                            'Type': ['Buy', 'Buy','Buy'] ,
#                            'Shares': [5, 10, 6],
#                            'Date': [buy_date_example,buy_date_example,buy_date_example]})

# Diseño de la aplicación con pestañas
app.layout = dbc.Container([
    # Primera fila
    dbc.Row([
        dbc.Col(
            html.H1(
                children=["Portfolio Manager"],
                id="titulo",
                style={
                    "text-align": "center",
                    # "backgroundColor": "#333",
                    "margin-bottom": "15px",
                    # "border-style": "outset",
                    # "border-color": "#333",
                    # "padding": "30px",
                    "height": "80px",
                    # "color": "#fff",
                    # "border-radius": "35px",
                },
            ),
        ),
    ]),

    # Pestañas
    dcc.Tabs([
        # Pestaña 1: Portfolio Movements
        dcc.Tab(label='Portfolio Movements', children=[
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Portfolio Movements", className="card-title"),
                            # Aquí irá la tabla de movimientos
                            dash_table.DataTable(
                                id='table_movements',
                                columns=[
                                    {'name': col, 'id': col, 'editable': True} for col in df_movements.columns
                                ],
                                data=df_movements.to_dict('records'),
                                style_table={'height': '400px', 'overflowY': 'auto'},
                            ),
                        ]),
                    ]),
                    width=12,
                ),
            ]),
        ]),

        # Pestaña 2: Evolution of my stocks
        dcc.Tab(label='Evolution of my stocks', children=[
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Evolution of my stocks", className="card-title"),
                            # Dropdown para seleccionar acciones en el gráfico
                            dcc.Dropdown(
                                id='stock_dropdown',
                                options=[{'label': ticker, 'value': ticker} for ticker in tickers],
                                value=tickers[0],  # Valor predeterminado
                                multi=False  # Solo permitir una selección
                            ),
                            # Gráfico de evolución de acciones
                            dcc.Graph(id='stock_evolution'),
                        ]),
                    ]),
                    width=12,
                ),
            ]),
        ]),

        dcc.Tab(label='Interactive Candlestick Chart', children=[
            html.Div([

                # Dropdown para seleccionar acciones en el gráfico
                dcc.Dropdown(
                    id='candlestick_stock_dropdown',
                    options=[{'label': ticker, 'value': ticker} for ticker in tickers],
                    value=tickers[0],  # Valor predeterminado
                    multi=False  # Solo permitir una selección
                ),
                # Rango de fechas para el gráfico de velas
                # dcc.DatePickerRange(
                #     id='candlestick_date_range',
                #     start_date=df_movements['Date'].min(),
                #     end_date=df_movements['Date'].max(),
                #     display_format='D/M/Y'
                # ),
                # Gráfico de velas interactivo
                dcc.Graph(id='candlestick_chart'),
            ]),
        ]),

        # Pestaña 3: Performance of my portfolio
        dcc.Tab(label='Performance of my portfolio', children=[
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Performance of my portfolio", className="card-title"),
                            # Botones para seleccionar el tipo de gráfico
                            dcc.RadioItems(
                                id='chart_selector',
                                options=[
                                    {'label': 'Overall Portfolio Performace', 'value': 'by_time'},
                                    {'label': 'Performance by Sector', 'value': 'by_sector'},
                                    {'label': 'Contribution of each Stock', 'value': 'contribution'}
                                ],
                                value='by_time',
                                labelStyle={'display': 'block'}
                            ),
                            # Gráfico correspondiente al tipo seleccionado
                            dcc.Graph(id='selected_chart'),
                        ]),
                    ]),
                    width=12,
                ),
            ]),
        ]),
    ])
], fluid=True, style={'font-family': 'Arial, sans-serif'})





# Callback para actualizar el gráfico de evolución de acciones
@app.callback(
    Output('stock_evolution', 'figure'),
    Input('stock_dropdown', 'value'),
    State('table_movements', 'data')
)
def update_stock_evolution(selected_stock, data):
    if not data or not selected_stock:
        # Si no hay datos o no hay acciones seleccionadas, no hay nada que mostrar
        return {'data': [], 'layout': {}}

    # Convertir la tabla de movimientos a un DataFrame
    df = pd.DataFrame(data)

    # Crear un DataFrame vacío para almacenar los datos de yfinance
    df_yfinance = pd.DataFrame()

    # Obtener datos históricos para el ticker seleccionado
    stock_data = ld.get_historical_data(selected_stock)

    # Añadir la columna 'Ticker' al DataFrame df
    stock_data['Ticker'] = selected_stock

    df_yfinance = pd.concat([df_yfinance, stock_data])

    predictions_prophet=p.train_and_predict(selected_stock)
    # predictions_prophet=predictions_prophet[-df_yfinance.size+30:]
    # print(prediction_data)

    predictions_linear_regression = lr.train_and_predict_linear_regression(selected_stock)


    traces = [
        {
            'x': df_yfinance['Date'],
            'y': df_yfinance['Close'],
            'name': selected_stock
        },
        {
            'x': predictions_prophet['ds'],
            'y': predictions_prophet['yhat'],
            'name': 'Prophet Prediction'
        },
        {
            'x': predictions_linear_regression['ds'],
            'y': predictions_linear_regression['yhat'],
            'name': 'Linear Regression Prediction'
        }
    ]

    # Diseño del gráfico
    fig = {
        'data': traces,
        'layout': {
            'title': f'Evolution of {selected_stock} with Price Predictions',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Close Price'},
            'legend': {'orientation': 'h'},
            'height': 1000  # Ajusta la altura según tus preferencias
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
        performance_data = sp.calculate_portfolio_performance(df_movements)

        traces = [
            {
                'x': performance_data.index,
                'y': performance_data['Cumulative Performance (%)'],
                'name': 'Portfolio Performance (%)'
            }
        ]

        # Diseño del gráfico
        fig = {
            'data': traces,
            'layout': {
                'title': 'Performance by Time',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Cumulative Performance (%)'},
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
        # Calcular la contribución de cada stock
        contribution_df = sp.calculate_stock_contribution(data)

        # Crear el gráfico de cascada
        fig = {
            'data': [
                {'x': contribution_df['Ticker'],
                 'y': contribution_df['Contribution'],
                 'type': 'waterfall',
                 'name': 'Contribución'}
            ],
            'layout': {
                'title': 'Contribution of Each Stock',
                'xaxis': {'title': 'Ticker'},
                'yaxis': {'title': 'Contribution'},
            }
        }

        return fig

    else:
        fig = {'data': [], 'layout': {}}

    return fig

# Callback para actualizar el gráfico de velas
@app.callback(
    Output('candlestick_chart', 'figure'),
    Input('candlestick_stock_dropdown', 'value'),
)
def update_candlestick_chart(selected_stock):
    if not selected_stock:
        return {'data': [], 'layout': {}}


    candlestick_data = get_candlestick_data(selected_stock)

    fig = go.Figure(data=[go.Candlestick(x=candlestick_data['x'],
                                         open=candlestick_data['open'],
                                         high=candlestick_data['high'],
                                         low=candlestick_data['low'],
                                         close=candlestick_data['close'])])

    fig.update_layout(title=f'Candlestick Chart for {selected_stock}',
                      xaxis_title='Date',
                      yaxis_title='Stock Price',
                      xaxis_rangeslider_visible=False)

    return fig

def get_candlestick_data(ticker):
    stock_data = ld.get_historical_data(ticker)

    candlestick_data = {
        'x': stock_data.index,
        'open': stock_data['Open'],
        'high': stock_data['High'],
        'low': stock_data['Low'],
        'close': stock_data['Close']
    }

    return candlestick_data

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
