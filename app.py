import dash
from dash import dcc, html, dash_table, Input, Output
import seaborn as sns
import plotly.express as px
import pandas as pd

# Load the dataset
url='https://drive.google.com/file/d/1r8_0OpvwHhsaC_e9hqmAHQWHjRr1Zbe9/view'
path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
df = pd.read_csv(path)

months = df['Month'].unique()
min_sent = df['Sentiment'].min()
max_sent = df['Sentiment'].max()
min_sub = df['Subjectivity'].min()
max_sub = df['Subjectivity'].max()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('Month:'),
            dcc.Dropdown(
                id='month', 
                options=[{'label': month, 'value': month} for month in months],
                value=months[0],
                className="dcc",
            ),
        ], className="filter"),
        html.Div([
            html.Label('Sentiment Score:'),
            dcc.RangeSlider(
                id='sentiment', 
                min=min_sent, 
                max=max_sent, 
                value=[min_sent, max_sent], 
                marks = {int(min_sent): str(min_sent), int(max_sent): str(max_sent)},
                className="dcc slider"         
            ),
        ], className="filter"),
        html.Div([
            html.Label('Subjectivity Score:'),
            dcc.RangeSlider(
                id='subjectivity', 
                min=min_sub, 
                max=max_sub, 
                value=[min_sub, max_sub], 
                marks = {int(min_sub): str(min_sub), int(max_sub): str(max_sub)},
                className="dcc slider"             
            ),
        ], className="filter")
    ], className="header"),
    html.Div(dcc.Graph(id='scatter'), className="graph"),
    html.Div(dash_table.DataTable(
            id='tweets',  # Assign ID to DataTable component
            columns=[{'name': 'RawTweet', 'id': 'RawTweet'}],
            data=[],
            page_size=10,
            page_current = 0,
            page_action='native',
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'whiteSpace': 'normal'},
        ), className="table-holder"),
], className="app")

@app.callback(Output('scatter', 'figure'), 
              [Input('month', 'value'), Input('sentiment', 'value'), Input('subjectivity', 'value')])
def update_graph(month_selected, sent_selected, sub_selected):
    if not sent_selected:
        sent_selected = [-1, 1]  # Default value if the slider is not set
    if not sub_selected:
        sub_selected = [0, 1]  # Default value if the slider is not set

    filtered_df = df[
        (df['Month'] == month_selected) &
        (df['Sentiment'] >= sent_selected[0]) &
        (df['Sentiment'] <= sent_selected[1]) &
        (df['Subjectivity'] >= sub_selected[0]) &
        (df['Subjectivity'] <= sub_selected[1])
    ]

    fig = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2', color_discrete_sequence=['gray'], opacity=0.5)
    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False,
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False,
        ),
        modebar={'orientation': 'v'}
    )
    return fig

@app.callback(Output('tweets', 'data'), 
              [Input('scatter', 'selectedData'),
               Input('tweets', 'page_current')])  # Added input for page_current
def display_selected_data(selected_data, current_page):
    if selected_data is not None:
        selected_points = selected_data['points']
        indices = [point['pointIndex'] for point in selected_points]
        selected_tweets = df.iloc[indices]['RawTweet']
        data = [{'RawTweet': tweet} for tweet in selected_tweets]
        return data
    else:
        return []

if __name__ == '__main__':
    app.run_server(debug=True)
