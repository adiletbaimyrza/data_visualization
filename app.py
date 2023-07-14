from dash import Dash, dcc, html, Output, Input
import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv('usgs-dataset.csv')

app = Dash(__name__)

app.layout = html.Div(id='main', children=[
    html.Link(
        rel='stylesheet',
        href='/assets/styles.css'
    ),
    html.Link(
        rel='preconnect',
        href='https://fonts.googleapis.com'
    ),
    html.Link(
        rel='preconnect',
        href='https://fonts.gstatic.com'
    ),
    html.Link(
        rel='stylesheet',
        href='https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap'
    ),
    html.Div(id='top-container', children=[
        html.Div(id='upper-left-container', children=[
            html.Div(id='RangeSlider-shares-container', children=[
                html.Div(id='RangeSlider-container', children=[
                    html.Div(id='mag-RangeSlider-container', className='container', children=[
                        dcc.RangeSlider(
                            id='mag-RangeSlider',
                            min=df['mag'].min(),
                            max=df['mag'].max(),
                            marks={},
                            value=[df['mag'].min(), df['mag'].max()],
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ]),
                    html.Div(id='year-RangeSlider-container', className='container', children=[
                        dcc.RangeSlider(
                            id='year-RangeSlider',
                            min=df['year'].min(),
                            max=df['year'].max(),
                            step=1,
                            marks={},
                            value=[df['year'].min(), df['year'].max()],
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ])
                ]),
                html.Div(id='shares-container', className='container', children=[
                    html.H5(id='shares-text', children=['shares of all earthquakes']),
                    html.H1(id='percentage', children=[])
                ])
            ]),
            html.Div(id='histogram-container', children=[
                html.Div(id='magType-container', className='container', children=[
                    dcc.Graph(
                        id='magType-histogram',
                        config={'displayModeBar': False, 'scrollZoom': True},
                        style={
                            #remove the whole styling to the css file
                            'padding-bottom': '2px',
                            'padding-left': '2px'}
                    )
                ]),
                html.Div(id='magSource-container', className='container', children=[
                    dcc.Graph(
                        id='magSource-histogram',
                        config={'displayModeBar': False, 'scrollZoom': True},
                        style={
                            'padding-bottom': '2px',
                            'padding-left': '2px'}
                    )
                ])
            ])
        ]),
        html.Div(id='upper-right-container', className='container', children=[
            dcc.Graph(
                id='map',
                config={'displayModeBar': False, 'scrollZoom': True},
                style={
                    'padding-bottom': '2px',
                    'padding-left': '2px'}
            )
        ])
    ]),
    html.Div(id='bottom-container', className='container', children=[
        dcc.Graph(
            id='mag-linechart',
            config={'displayModeBar': False, 'scrollZoom': True},
            style={'padding-bottom': '2px', 'padding-left': '2px'}
        )
    ])
])


@app.callback(
    Output('map', 'figure'),
    Output('mag-linechart', 'figure'),
    Output('magType-histogram', 'figure'),
    Output('magSource-histogram', 'figure'),
    Output('percentage', 'children'),  # Updated the id to match the HTML element
    Input('mag-RangeSlider', 'value'),
    Input('year-RangeSlider', 'value'),
    Input('map', 'relayoutData')
)
def update_data(mag_range, year_range, relayoutData):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
                    (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

    filtered_data_percentage = len(filtered_df) / len(df) * 100

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

    map_figure = go.Figure(data=go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        mode='markers',
        marker=dict(size=filtered_df['bubble_size'], color=filtered_df['color']),
        text=filtered_df['mag'],
        hovertemplate='Magnitude: %{text}<br>Latitude: %{lat}<br>Longitude: %{lon}<extra></extra>'
    ))

    map_figure.update_layout(
        mapbox=dict(
            #style=os.getenv('MAPBOX_STYLE'),
            accesstoken=os.getenv('MAPBOX_TOKEN'),
            center=dict(lat=filtered_df['latitude'].mean(), lon=filtered_df['longitude'].mean()),
            zoom=2,
            uirevision=True
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    magType_histogram = go.Figure(data=go.Histogram(
        x=filtered_df['magType'],
        marker=dict(color='blue')
    ))
    magType_histogram.update_layout(title='Magnitude Type Distribution')

    magSource_histogram = go.Figure(data=go.Histogram(
        x=filtered_df['magSource'],
        marker=dict(color='blue')
    ))
    magSource_histogram.update_layout(title='Net Distribution')

    mag_linechart = go.Figure(data=go.Histogram(
        x=filtered_df['mag'],
        nbinsx=30,
        marker=dict(color='blue')
    ))
    mag_linechart.update_layout(title='Magnitude Distribution', xaxis_title='Magnitude', yaxis_title='Count')

    return map_figure, mag_linechart, magType_histogram, magSource_histogram, f"{filtered_data_percentage:.2f}%"  # Display percentage with two decimal places



if __name__ == '__main__':
    app.run_server(debug=False)
