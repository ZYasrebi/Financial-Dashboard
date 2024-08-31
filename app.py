import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go



# Lists of stocks in different sectors
hardware_tickers = ['AAPL', 'NVDA', 'INTC']
software_tickers = ['MSFT', 'ORCL', 'ADBE']
digital_media_tickers = ['GOOGL', 'META', 'NFLX']
crypto_tickers = ['BTC-USD', 'DOGE-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD']  # Cryptocurrencies

# Download data for S&P 500 and NASDAQ
index_tickers = ['^GSPC', '^IXIC']  # S&P 500 and NASDAQ
index_data = yf.download(index_tickers, period="5d")
index_data = index_data.ffill().bfill()

# Function to fetch stock data
def fetch_stock_data(tickers):
    data = yf.download(tickers, period="5d")
    data = data.ffill().bfill()
    return data

# Function to fetch stock data for line chart
def fetch_stock_data_line_chart(tickers, period="5d"):
    data = yf.download(tickers, period=period)
    data = data.ffill().bfill()
    return data

#line chart variables
line_chart_top_companies = ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN']
top_companies_data = fetch_stock_data_line_chart(line_chart_top_companies, period="5y")['Close'] 

# Fetch data for each sector and cryptocurrencies
hardware_data = fetch_stock_data(hardware_tickers)
software_data = fetch_stock_data(software_tickers)
digital_media_data = fetch_stock_data(digital_media_tickers)
crypto_data = fetch_stock_data(crypto_tickers)


# Combine all data
all_data = pd.concat([hardware_data, software_data, digital_media_data, crypto_data], axis=1)

# Calculate percentage change for the last day
pct_change = all_data['Close'].pct_change().iloc[-1] * 100

# Identify bullish and bearish stocks
bullish_stocks = pct_change[pct_change > 0].sort_values(ascending=False)
bearish_stocks = pct_change[pct_change < 0].sort_values(ascending=False)

# Select top 10 growth stocks
top_growth_stocks = pct_change.sort_values(ascending=False).head(10)

# Extract important metrics for each sector
def extract_metrics(tickers):
    metrics = {}
    for ticker in tickers:
        stock_info = yf.Ticker(ticker).info
        metrics[ticker] = {
            'Market Cap': pd.to_numeric(stock_info.get('marketCap', 0), errors='coerce'),
            'P/E Ratio': pd.to_numeric(stock_info.get('trailingPE', 0), errors='coerce'),
            'Volume': pd.to_numeric(stock_info.get('volume', 0), errors='coerce'),
            'EPS (ttm)': pd.to_numeric(stock_info.get('trailingEps', 0), errors='coerce'),
            '52 Week High': pd.to_numeric(stock_info.get('fiftyTwoWeekHigh', 0), errors='coerce'),
            'Sales Y/Y': pd.to_numeric(stock_info.get('revenueGrowth', 0), errors='coerce'),
            'Profit Margin': pd.to_numeric(stock_info.get('profitMargins', 0), errors='coerce'),
            'Target Price': pd.to_numeric(stock_info.get('targetMeanPrice', 0), errors='coerce'),
            '52 Week Low': pd.to_numeric(stock_info.get('fiftyTwoWeekLow', 0), errors='coerce'),
            'EPS Y/Y TTM': pd.to_numeric(stock_info.get('earningsGrowth', 0), errors='coerce'),
            'Forward P/E': pd.to_numeric(stock_info.get('forwardPE', 0), errors='coerce'),
            'Beta': pd.to_numeric(stock_info.get('beta', 0), errors='coerce'),
            'Avg Volume': pd.to_numeric(stock_info.get('averageVolume', 0), errors='coerce')
        }
    return pd.DataFrame(metrics).T

hardware_metrics = extract_metrics(hardware_tickers)
software_metrics = extract_metrics(software_tickers)
digital_media_metrics = extract_metrics(digital_media_tickers)
crypto_metrics = extract_metrics(crypto_tickers)  # For cryptocurrencies

# Adding S&P 500 and NASDAQ indices to the data
index_metrics = extract_metrics(index_tickers)

# Start building the Dash app
app = dash.Dash(__name__)

# مسیر به فایل favicon
app._favicon = "assets/favicon.ico"

app.layout = html.Div(style={'backgroundColor': '#2E2E2E', 'color': 'white', 'fontFamily': 'Arial'}, children=[
    html.Link(href='https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css', rel='stylesheet'),
    
    # Buttons for Bullish, Bearish, Top 10 Growth Stocks, and Cryptocurrencies
    html.Div([
        html.Button('Bullish Stocks', id='bullish-button', n_clicks=0, className='btn btn-success',
                    style={'margin': '10px', 'borderRadius': '5px', 'color': '#2E2E2E', 'backgroundColor': '#5CDB95'}),
        html.Button('Bearish Stocks', id='bearish-button', n_clicks=0, className='btn btn-danger',
                    style={'margin': '10px', 'borderRadius': '5px', 'color': '#2E2E2E', 'backgroundColor': '#FC4445'}),
        html.Button('Top 10 Growth Stocks', id='top10-button', n_clicks=0, className='btn btn-primary',
                    style={'margin': '10px', 'borderRadius': '5px', 'color': '#2E2E2E', 'backgroundColor': '#3B9AE1'}),
        html.Button('Cryptocurrencies', id='crypto-button', n_clicks=0, className='btn btn-warning',
                    style={'margin': '10px', 'borderRadius': '5px', 'color': '#2E2E2E', 'backgroundColor': '#FFD700'})
    ], className='button-group', style={'textAlign': 'center', 'padding': '20px'}),

    html.Div(id='summary-content', style={'padding': '20px', 'textAlign': 'center'}),

    # Dropdowns and chart for sector and metrics comparison
    html.Div([
        dcc.Dropdown(
            id='sector-selector',
            options=[
                {'label': 'Hardware', 'value': 'Hardware'},
                {'label': 'Software', 'value': 'Software'},
                {'label': 'Digital Media & Online Advertising', 'value': 'Digital Media'}
            ],
            value=['Hardware'],  # Default value
            multi=True,  # Allow multiple selections
            className='dropdown',
            style={'backgroundColor': '#FFF', 'color': '#000', 'border': '1px solid #CCC', 'borderRadius': '4px', 'padding': '5px', 'marginBottom': '10px'}
        ),
        
        dcc.Dropdown(
            id='metric-selector',
            options=[
                {'label': 'Market Cap', 'value': 'Market Cap'},
                {'label': 'P/E Ratio', 'value': 'P/E Ratio'},
                {'label': 'Volume', 'value': 'Volume'},
                {'label': 'EPS (ttm)', 'value': 'EPS (ttm)'},
                {'label': '52 Week High', 'value': '52 Week High'},
                {'label': 'Sales Y/Y', 'value': 'Sales Y/Y'},
                {'label': 'Profit Margin', 'value': 'Profit Margin'},
                {'label': 'Target Price', 'value': 'Target Price'},
                {'label': '52 Week Low', 'value': '52 Week Low'},
                {'label': 'EPS Y/Y TTM', 'value': 'EPS Y/Y TTM'},
                {'label': 'Forward P/E', 'value': 'Forward P/E'},
                {'label': 'Price', 'value': 'Price'}
            ],
            value='Market Cap',  # Default value
            className='dropdown',
            style={'backgroundColor': '#FFF', 'color': '#000', 'border': '1px solid #CCC', 'borderRadius': '4px', 'padding': '5px', 'marginBottom': '10px'}
        ),
        
        dcc.Dropdown(
            id='timeframe-selector',
            options=[
                {'label': '1 Minute', 'value': '1m'},
                {'label': '5 Minutes', 'value': '5m'},
                {'label': '15 Minutes', 'value': '15m'},
                {'label': '30 Minutes', 'value': '30m'},
                {'label': '4 Hours', 'value': '4h'},
                {'label': 'Daily', 'value': '1d'},
                {'label': 'Weekly', 'value': '1wk'},
                {'label': 'Monthly', 'value': '1mo'},
                {'label': '3 Months', 'value': '3mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '3 Years', 'value': '3y'},
                {'label': '5 Years', 'value': '5y'}
            ],
            value='1d',  # Default value
            className='dropdown',
            style={'backgroundColor': '#FFF', 'color': '#000', 'border': '1px solid #CCC', 'borderRadius': '4px', 'padding': '5px', 'marginBottom': '20px'}
        ),

        dcc.Checklist(
            id='compare-indexes',
            options=[
                {'label': 'Compare with S&P 500', 'value': '^GSPC'},
                {'label': 'Compare with NASDAQ', 'value': '^IXIC'}
            ],
            value=[],
            style={'color': 'white'}
        ),
        
        dcc.Graph(id='comparison-chart')
    ], className='container', style={'backgroundColor': '#2E2E2E', 'color': 'white', 'marginBottom': '60px'}),
  
    
     # Dropdown for selecting companies and line chart for growth
    html.Div([

        html.Div([
            html.Div([
                html.Hr(style={'backgroundColor':'#FFF', 'marginBottom':'60px'}),
            ], className='col'),
        ], className='row'),

        html.Div([
            html.Div([
                html.H3(style={'marginBottom':'30px'}),
            ], className='col'),
        ], className='row'),

        html.Div([

            html.Div([
                dcc.Dropdown(
                            id='line-chart-company-selector',
                            options=[{'label': company, 'value': company} for company in line_chart_top_companies],
                            value=line_chart_top_companies,  # Default value to show all companies
                            multi=True,  # Allow multiple selections
                            className='dropdown',
                            style={'color': '#000', 'borderRadius': '4px', 'padding': '5px', 'marginBottom': '10px'}
                        ),
            ], className='col'),
            html.Div([
                dcc.Dropdown(
                            id='line-chart-comparison-selector',
                            options=[{'label': company, 'value': company} for company in line_chart_top_companies],
                            value=line_chart_top_companies[0],  # Default comparison company
                            style={'color': '#000', 'borderRadius': '4px', 'padding': '5px', 'marginBottom': '10px'}
                        ),
            ], className='col')
        ], className='row'),

        html.Div([
            html.Div([
                dcc.Checklist(
                                id='line-chart-aggregate-selector',
                                options=[
                                    {'label': 'Aggregate Growth', 'value': 'aggregate'}
                                ],
                                value=[],  # Default value is not checked
                                style={'color': '#FFF', 'margin': '10px'}
                            ),
            ], className='col'),
            
        ], className='row'),
        
        
       

       

       

        dcc.Graph(id='line-chart', className='graph-container', style={'backgroundColor': '#000000'})
    ], className='container', style={'color': 'white'})
])

@app.callback(
    Output('summary-content', 'children'),
    [Input('bullish-button', 'n_clicks'),
     Input('bearish-button', 'n_clicks'),
     Input('top10-button', 'n_clicks'),
     Input('crypto-button', 'n_clicks')]
)
def update_summary(bullish_clicks, bearish_clicks, top10_clicks, crypto_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return "Click a button to see the stocks."
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'bullish-button':
        return dash_table.DataTable(
            columns=[{'name': 'Bullish Stocks', 'id': 'Stock'}, {'name': 'Change %', 'id': 'Change %'}],
            data=[{'Stock': stock, 'Change %': f"{round(change, 2)}%"} for stock, change in bullish_stocks.items() if not stock.endswith('-USD')],
            style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#333', 'color': 'white'},
            style_header={'backgroundColor': '#444', 'fontWeight': 'bold'},
            style_table={'width': '25%', 'margin': '0 auto'}  # عرض جدول کاهش داده شده
        )
    elif button_id == 'bearish-button':
        return dash_table.DataTable(
            columns=[{'name': 'Bearish Stocks', 'id': 'Stock'}, {'name': 'Change %', 'id': 'Change %'}],
            data=[{'Stock': stock, 'Change %': f"{round(change, 2)}%"} for stock, change in bearish_stocks.items() if not stock.endswith('-USD')],
            style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#333', 'color': 'white'},
            style_header={'backgroundColor': '#444', 'fontWeight': 'bold'},
            style_table={'width': '25%', 'margin': '0 auto'}  # عرض جدول کاهش داده شده
        )
    elif button_id == 'top10-button':
        return dash_table.DataTable(
            columns=[{'name': 'Top 10 Growth Stocks', 'id': 'Stock'}, {'name': 'Change %', 'id': 'Change %'}],
            data=[{'Stock': stock, 'Change %': f"{round(change, 2)}%"} for stock, change in top_growth_stocks.items() if not stock.endswith('-USD')],
            style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#333', 'color': 'white'},
            style_header={'backgroundColor': '#444', 'fontWeight': 'bold'},
            style_table={'width': '25%', 'margin': '0 auto'}  # عرض جدول کاهش داده شده
        )
    elif button_id == 'crypto-button':
        return dash_table.DataTable(
            columns=[{'name': 'Cryptocurrencies', 'id': 'Cryptocurrencies'}, {'name': 'Change %', 'id': 'Change %'}],
            data=[{'Cryptocurrencies': crypto, 'Change %': f"{round(change, 2)}%"} for crypto, change in pct_change.items() if crypto.endswith('-USD')],
            style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#333', 'color': 'white'},
            style_header={'backgroundColor': '#444', 'fontWeight': 'bold'},
            style_table={'width': '25%', 'margin': '0 auto'}  # عرض جدول کاهش داده شده
        )
    return None

@app.callback(
    Output('comparison-chart', 'figure'),
    [Input('sector-selector', 'value'),
     Input('metric-selector', 'value'),
     Input('timeframe-selector', 'value'),
     Input('compare-indexes', 'value')]
)
def update_chart(selected_sectors, selected_metric, selected_timeframe, compare_indexes):
    # Select data for the chosen sectors
    filtered_dfs = []
    overall_metrics = {}
    for sector in selected_sectors:
        if sector == 'Hardware':
            filtered_dfs.append(hardware_metrics)
            overall_metrics['Hardware Overall'] = hardware_metrics.mean()
        elif sector == 'Software':
            filtered_dfs.append(software_metrics)
            overall_metrics['Software Overall'] = software_metrics.mean()
        elif sector == 'Digital Media':
            filtered_dfs.append(digital_media_metrics)
            overall_metrics['Digital Media Overall'] = digital_media_metrics.mean()
    
    filtered_df = pd.concat(filtered_dfs)
    
    # Add overall metrics if specific sectors are selected
    if 'Hardware' in selected_sectors:
        filtered_df = pd.concat([filtered_df, pd.DataFrame(overall_metrics['Hardware Overall'], columns=['Hardware Overall']).T])
    if 'Software' in selected_sectors:
        filtered_df = pd.concat([filtered_df, pd.DataFrame(overall_metrics['Software Overall'], columns=['Software Overall']).T])
    if 'Digital Media' in selected_sectors:
        filtered_df = pd.concat([filtered_df, pd.DataFrame(overall_metrics['Digital Media Overall'], columns=['Digital Media Overall']).T])

    # Add S&P 500 and NASDAQ indices for comparison (if selected)
    if compare_indexes:
        for index in compare_indexes:
            filtered_df = pd.concat([filtered_df, index_metrics.loc[[index]]])

    # Convert metric to numeric for plotting
    filtered_df[selected_metric] = pd.to_numeric(filtered_df[selected_metric], errors='coerce')
    filtered_df = filtered_df.dropna(subset=[selected_metric])

    # Create comparison chart based on the selected metric
    comparison_fig = px.bar(
        filtered_df,
        x=filtered_df.index,
        y=selected_metric,
        color=filtered_df.index,
        title=f"Comparison of {selected_metric} in Selected Sectors",
        template='plotly_dark'  # تم جدید با رنگ تیره اما روشن‌تر
    )

    return comparison_fig


# Callback to update the line chart based on company selection, aggregation option, and comparison company
@app.callback(
    Output('line-chart', 'figure'),
    [Input('line-chart-company-selector', 'value'),
     Input('line-chart-aggregate-selector', 'value'),
     Input('line-chart-comparison-selector', 'value')]
)
def update_line_chart(selected_companies, aggregate_option, comparison_company):
    if not selected_companies:
        return {}

    fig = go.Figure()

    if 'aggregate' in aggregate_option:
        if len(selected_companies) > 2:
            top_companies_subset = [comp for comp in selected_companies if comp != comparison_company]
            avg_prices = top_companies_data[top_companies_subset].mean(axis=1)
            fig.add_trace(go.Scatter(x=top_companies_data.index, y=avg_prices, mode='lines', name='Average of Selected'))

            if comparison_company:
                fig.add_trace(go.Scatter(x=top_companies_data.index, y=top_companies_data[comparison_company], mode='lines', name=comparison_company))
        else:
            fig.add_trace(go.Scatter(x=top_companies_data.index, y=top_companies_data[selected_companies[0]], mode='lines', name='Selected Company'))
    else:
        for company in selected_companies:
            fig.add_trace(go.Scatter(x=top_companies_data.index, y=top_companies_data[company], mode='lines', name=company))

    fig.update_layout(title='5-Year Growth of Top Companies', xaxis_title='Date', yaxis_title='Stock Price',
                      plot_bgcolor='#2E2E2E', paper_bgcolor='#2E2E2E', font_color='white')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
