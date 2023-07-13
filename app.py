from dash import Dash, dcc, html, Output, Input
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('earthquakes.csv')

app = Dash(__name__)

app.layout = html.Div([
    dcc.RangeSlider(
        id='mag-RangeSlider',
        min=df['mag'].min(),
        max=df['mag'].max(),
        marks={},
        value=[df['mag'].min(), df['mag'].max()],
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    dcc.RangeSlider(
        id='year-RangeSlider',
        min=df['year'].min(),
        max=df['year'].max(),
        step=1,
        marks={},
        value=[df['year'].min(), df['year'].max()],
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Div(id='filtered-data-info'),

    dcc.Graph(
        id='graph',
        config={'displayModeBar': False, 'scrollZoom': True},
        style={'background': '#00FC87', 'padding-bottom': '2px', 'padding-left': '2px', 'height': '50vh'}
    ),
    
    dcc.Graph(
        id='histogram-1',
        config={'displayModeBar': False, 'scrollZoom': True},
        style={'background': '#00FC87', 'padding-bottom': '2px', 'padding-left': '2px', 'height': '25vh'}
    ),

    dcc.Graph(
        id='histogram-2',
        config={'displayModeBar': False, 'scrollZoom': True},
        style={'background': '#00FC87', 'padding-bottom': '2px', 'padding-left': '2px', 'height': '25vh'}
    )
])

@app.callback(Output('graph', 'figure'),
              Output('histogram-1', 'figure'),
              Output('histogram-2', 'figure'),
              Output('filtered-data-info', 'children'),
              Input('mag-RangeSlider', 'value'),
              Input('year-RangeSlider', 'value'),
              Input('graph', 'relayoutData'))
def update_graph(mag_range, year_range, relayoutData):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
                     (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    filtered_data_percentage = len(filtered_df) / len(df) * 100
    filtered_data_info = f"Filtered Data: {len(filtered_df)} out of {len(df)} earthquakes ({filtered_data_percentage:.2f}%)"

    # Check if relayoutData exists and contains a selection shape
    if relayoutData and 'shapes' in relayoutData:
        shapes = relayoutData['shapes']
        if shapes:
            shape = shapes[0]  # Assuming only one shape is selected
            if shape['type'] == 'rect':
                x0, y0, x1, y1 = shape['x0'], shape['y0'], shape['x1'], shape['y1']
                lat_min, lat_max = y0, y1
                lon_min, lon_max = x0, x1
                filtered_df = filtered_df[(filtered_df['latitude'] >= lat_min) & (filtered_df['latitude'] <= lat_max) &
                                          (filtered_df['longitude'] >= lon_min) & (filtered_df['longitude'] <= lon_max)]

    figure = go.Figure(data=go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        mode='markers',
        marker=dict(size=5, color=filtered_df['mag'], colorscale='Rainbow', showscale=True),
        text=filtered_df['mag'],
        hovertemplate='Magnitude: %{text}<br>Latitude: %{lat}<br>Longitude: %{lon}<extra></extra>'
    ))

    figure.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=filtered_df['latitude'].mean(), lon=filtered_df['longitude'].mean()),
            zoom=2
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        width=500
    )

    histogram_1 = go.Figure(data=go.Histogram(
        x=filtered_df['magType'],
        marker=dict(color='blue')
    ))
    histogram_1.update_layout(title='Magnitude Type Distribution')

    histogram_2 = go.Figure(data=go.Histogram(
        x=filtered_df['net'],
        marker=dict(color='blue')
    ))
    histogram_2.update_layout(title='Net Distribution')

    return figure, histogram_1, histogram_2, filtered_data_info


if __name__ == '__main__':
    app.run_server(debug=True)
