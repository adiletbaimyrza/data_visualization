from dash import Dash, dcc, html
import pandas as pd

df = pd.read_csv('earthquakes.csv')

app = Dash(__name__)

app.layout = html.Div([
    dcc.RangeSlider(
        df['mag'].min(),
        df['mag'].max(), 
        value=[df['mag'].min(), df['mag'].max()],
        tooltip={"placement": "bottom", "always_visible": True},
        id='mag-RangeSlider'
    ),
    # dcc.Graph(bla bla bla)
])

if __name__ == '__main__':
    app.run(debug=True)
