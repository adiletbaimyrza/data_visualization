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
                            marks=None,
                            value=[df['mag'].min(), df['mag'].max()],
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ]),
                    html.Div(
                            id='year-RangeSlider-container',
                            className='container',
                            children=[
                                dcc.RangeSlider(
                                    id='year-RangeSlider',
                                    min=df['year'].min(),
                                    max=df['year'].max(),
                                    step=1,
                                    value=[df['year'].min(), df['year'].max()],
                                    tooltip={"placement": "bottom", "always_visible": True},
                                    marks=None
                                )
                            ]
                    )           
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
                        config={'displayModeBar': False, 'staticPlot': True},
                    )
                ]),
                html.Div(id='magSource-container', className='container', children=[
                    dcc.Graph(
                        id='magSource-histogram',
                        config={'displayModeBar': False,
                                'scrollZoom': False,
                                'editable': False,
                                'showAxisDragHandles': False,
                                'showAxisRangeEntryBoxes': False, 
                                'showTips': True,
                                'staticPlot': True}
                    )
                ])
            ])
        ]),
        html.Div(id='upper-right-container', className='container', children=[
            dcc.Graph(
                id='map',
                config={'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False},
                selectedData={}
            )
        ]),
    ]),
    html.Div(id='bottom-container', className='container', children=[
            dcc.Graph(
                id='mag-linechart',
                config={'displayModeBar': False, 'staticPlot': True}
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
    Input('map', 'selectedData')
)
def update_data(mag_range, year_range, selectedData):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
                    (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

    filtered_data_percentage = len(filtered_df) / len(df) * 100

    map_figure = go.Figure(data=go.Scattermapbox(
        lat=filtered_df['latitude'],
        lon=filtered_df['longitude'],
        mode='markers',
        marker=dict(size=filtered_df['bubble_size'], color=filtered_df['color']),
        text=filtered_df['mag'],
        hovertemplate='Magnitude: %{text}<br>Latitude: %{lat}<br>Longitude: %{lon}<extra></extra>',
        
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
    
    magType_counts = filtered_df['magType'].value_counts()
    top_magTypes = magType_counts.nlargest(3).index
    filtered_df_top_magTypes = filtered_df[filtered_df['magType'].isin(top_magTypes)]

    magType_histogram = go.Figure(data=go.Histogram(
        x=filtered_df_top_magTypes['magType'],
        marker=dict(color='blue')
    ))
    magType_histogram.update_layout()
    
    magSource_counts = filtered_df['magSource'].value_counts()
    top_magSources = magSource_counts.nlargest(3).index
    filtered_df_top_magSources = filtered_df[filtered_df['magSource'].isin(top_magSources)]

    magSource_histogram = go.Figure(data=go.Histogram(
        x=filtered_df_top_magSources['magSource'],
        marker=dict(color='blue')
    ))
    magSource_histogram.update_layout()
    
    mag_linechart = go.Figure(data=go.Histogram(
        x=filtered_df['mag'],
        nbinsx=30,
        marker=dict(color='blue')
    ))
    mag_linechart.update_layout()


    return map_figure, mag_linechart, magType_histogram, magSource_histogram, f"{filtered_data_percentage:.2f}%"  # Display percentage with two decimal places



if __name__ == '__main__':
    app.run_server(debug=False)
