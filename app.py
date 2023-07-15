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
    html.Div(id='grid-container', children=[
        html.Div(id='mag-RangeSlider-container', className='container', children=[
            html.P('Magnitude'),
            dcc.RangeSlider(
                id='mag-RangeSlider',
                className='display-item',
                min=df['mag'].min(),
                max=df['mag'].max(),
                marks=None,
                value=[df['mag'].min(), df['mag'].max()],
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ]),
        html.Div(id='year-RangeSlider-container', className='container', children=[
            html.P('Year'),
            dcc.RangeSlider(
                id='year-RangeSlider',
                className='display-item',
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                value=[df['year'].min(), df['year'].max()],
                tooltip={"placement": "bottom", "always_visible": True},
                marks=None
            )
        ]),
        html.Div(id='shares-container', className='container', children=[
                    html.H5(id='shares-text', children=['Share of all earthquakes']),
                    html.H1(id='percentage', children=[])
        ]),
        html.Div(id='magType-container', className='container', children=[
            html.P('Top magnitude types'),
            dcc.Graph(
                id='magType-histogram',
                className='display-item',
                config={'displayModeBar': False, 'staticPlot': True, 'responsive': True},
                figure={'layout': {'autosize': True}},
            )
        ]),
        html.Div(id='magSource-container', className='container', children=[
            html.P('Top contributors'),
            dcc.Graph(
                id='magSource-histogram',
                className='display-item',
                config={'displayModeBar': False,
                        'scrollZoom': False,
                        'staticPlot': True},
                responsive=True
            )
        ]),
        html.Div(id='mag-linechart-container', className='container', children=[
            html.P('Earthquakes distribution by magnitude'),
            dcc.Graph(
                id='mag-linechart',
                className='display-item',
                config={'displayModeBar': False, 'staticPlot': True},
                responsive=True
            )
        ]),
        html.Div(id='map-container', className='container', children=[
            dcc.Graph(
                id='map',
                className='display-item',
                config={'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False},
                selectedData={}
            )
        ])
    ])
])


@app.callback(
    Output('map', 'figure'),
    Output('mag-linechart', 'figure'),
    Output('magType-histogram', 'figure'),
    Output('magSource-histogram', 'figure'),
    Output('percentage', 'children'),
    Input('mag-RangeSlider', 'value'),
    Input('year-RangeSlider', 'value'),
    Input('map', 'selectedData')
)
def update_data(mag_range, year_range, selectedData):
    filtered_df = df[(df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
                    (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    if selectedData:
        selected_points = selectedData.get('points', [])
        if selected_points:
            selected_indices = [point.get('pointIndex') for point in selected_points]
            filtered_df = filtered_df.iloc[selected_indices]
            
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
        margin=dict(l=3, r=3, t=3, b=3))
    
    magType_counts = filtered_df['magType'].value_counts()
    top_magTypes = magType_counts.nlargest(3).index
    filtered_df_top_magTypes = filtered_df[filtered_df['magType'].isin(top_magTypes)]
    
    magType_histogram = go.Figure(data=go.Histogram(
        x=filtered_df_top_magTypes['magType'],
        marker=dict(color='rgb(46, 116, 173)'),
        
    ))
    magType_histogram.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                    plot_bgcolor='rgb(37, 44, 61)',
                                    paper_bgcolor='rgb(37, 44, 61)',
                                    font_color='white')
    
    magSource_counts = filtered_df['magSource'].value_counts()
    top_magSources = magSource_counts.nlargest(3).index
    filtered_df_top_magSources = filtered_df[filtered_df['magSource'].isin(top_magSources)]
    
    magSource_histogram = go.Figure(data=go.Histogram(
        x=filtered_df_top_magSources['magSource'],
        marker=dict(color='rgb(46, 116, 173)')
    ))
    magSource_histogram.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                    plot_bgcolor='rgb(37, 44, 61)',
                                    paper_bgcolor='rgb(37, 44, 61)',
                                    font_color='white')
    
    mag_linechart = go.Figure(data=go.Histogram(
        x=filtered_df['mag'],
        nbinsx=30,
        marker=dict(color='rgb(46, 116, 173)')
    ))
    mag_linechart.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                plot_bgcolor='rgb(37, 44, 61)',
                                paper_bgcolor='rgb(37, 44, 61)',
                                font_color='white')
    
    return map_figure, mag_linechart, magType_histogram, magSource_histogram, f"{filtered_data_percentage:.2f}%"  # Display percentage with two decimal places


if __name__ == '__main__':
    app.run_server(debug=False)