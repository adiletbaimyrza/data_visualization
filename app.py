from dash import Dash, dcc, html

app = Dash(__name__)

app.layout = html.Div([
    dcc.RangeSlider(-5, 10, 1, count=1, value=[-3, 7])
])

if __name__ == '__main__':
    app.run(debug=True)
