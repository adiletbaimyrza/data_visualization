import os
import pandas as pd
from dotenv import load_dotenv
import plotly.graph_objects as go
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from dash import Dash, dcc, html, Output, Input


external_stylesheets = [
    {'href': '/assets/css/sliders.css', 'rel': 'stylesheet'},
    {'href': '/assets/css/button.css', 'rel': 'stylesheet'},
    {'href': '/assets/css/message.css', 'rel': 'stylesheet'},
]

PLOT_BGCOLOR='#373432'
PAPER_BGCOLOR='#373432'
FONT_COLOR='white'
MARKER_COLOR='#00cbff'

MESSAGE="""Welcome to the earthquake data visualization website!This platform allows
            you to observe and delve into more than 8000+ significant earthquakes
            (with a magnitude of 6 or higher) recorded from January 1st, 1960, until July 16th, 2023.
            Among the notable earthquakes you can find here are 2011 Tohoku Earthquake,
            Japan and the 1960 Great Valvidia Earthquake, Chile.
            Made by Adilet Baimyrza."""

df = pd.read_csv('data_visualization/data/usgs-dataset.csv')

load_dotenv()

app = Dash(__name__,
            external_stylesheets=external_stylesheets,
            meta_tags=[{"name": "viewport",
                        "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no"}])

server = app.server

app.title = 'Earthquake Data Visualization Dashboard'
app.layout = html.Div(id='main', children=[
    html.Link(
        rel='stylesheet',
        href='/assets/css/styles.css'
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
        dmc.NotificationsProvider(
            position='top-center',
            containerWidth=800,
            children=
            html.Div(id='info', className='container', children=[
                    html.Div(id="info-container"),
                    dmc.Button("Details",
                                rightIcon=DashIconify(icon='octicon:info-16', width=20),
                                id="info-button",
                                variant='filled',
                                fullWidth=True,
                                radius=0
                    )
            ])
        ),
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
        html.Div(id='map-container', className='container', children=[
            dcc.Graph(
                id='map',
                className='display-item',
                config={'displayModeBar': 'hover',
                        'scrollZoom': True,
                        'displaylogo': False},
                selectedData={}
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
                config={'displayModeBar': False,
                        'staticPlot': True,
                        'responsive': True}
            )
        ]),
        html.Div(id='magSource-container', className='container', children=[
            html.P('Top contributors'),
            dcc.Graph(
                id='magSource-histogram',
                className='display-item',
                config={'displayModeBar': False,
                        'staticPlot': True,
                        'responsive': True}
            )
        ]),
        html.Div(id='mag-linechart-container', className='container', children=[
            html.P('Earthquakes distribution by magnitude'),
            dcc.Graph(
                id='mag-linechart',
                className='display-item',
                config={'displayModeBar': False,
                        'staticPlot': True,
                        'responsive': True}
            )
        ])
    ])
])


@app.callback(
    Output("info-container", "children"),
    Input("info-button", "n_clicks")
)
def show(n_clicks):
    return dmc.Notification(
        autoClose=False,
        title="Earthquake Data Visualization Dashboard",
        id="info-message",
        action="show",
        message=MESSAGE,
        icon=DashIconify(icon="icon-park-outline:owl")
)


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
    
    
    map_figure = go.Figure(
        data=go.Scattermapbox(
            lat=filtered_df['latitude'],
            lon=filtered_df['longitude'],
            mode='markers',
            marker=dict(size=filtered_df['bubble_size'], color=filtered_df['color'], opacity=0.7),
            text=filtered_df['mag'],
            customdata=filtered_df[['place', 'year', 'depth']],
            hovertemplate='Magnitude: %{text}<br>Place: %{customdata[0]}<br>Year: %{customdata[1]}<br>Depth: %{customdata[2]}km<extra></extra>',
        )
    )
    map_figure.update_layout(
        mapbox=dict(
            accesstoken=os.getenv('MAPBOX_TOKEN'),
            zoom=2,
            uirevision=True,
            style='dark'
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    
    magType_counts = filtered_df['magType'].value_counts()
    top_magTypes = magType_counts.nlargest(3).index
    filtered_df_top_magTypes = filtered_df[filtered_df['magType'].isin(top_magTypes)]
    
    magType_histogram = go.Figure(
        data=go.Histogram(
            x=filtered_df_top_magTypes['magType'],
            marker=dict(color=MARKER_COLOR)
        )
    )
    magType_histogram.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                    plot_bgcolor=PLOT_BGCOLOR,
                                    paper_bgcolor=PAPER_BGCOLOR,
                                    font_color=FONT_COLOR,
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False))
    
    
    magSource_counts = filtered_df['magSource'].value_counts()
    top_magSources = magSource_counts.nlargest(3).index
    filtered_df_top_magSources = filtered_df[filtered_df['magSource'].isin(top_magSources)]
    
    magSource_histogram = go.Figure(
        data=go.Histogram(
            x=filtered_df_top_magSources['magSource'],
            marker=dict(color=MARKER_COLOR)
        )
    )
    magSource_histogram.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                    plot_bgcolor=PLOT_BGCOLOR,
                                    paper_bgcolor=PAPER_BGCOLOR,
                                    font_color=FONT_COLOR,
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False))
    
    
    mag_linechart = go.Figure(
        data=go.Histogram(
            x=filtered_df['mag'],
            nbinsx=30,
            marker=dict(color=MARKER_COLOR)
        )
    )
    mag_linechart.update_layout(margin=dict(l=3, r=3, t=3, b=3),
                                plot_bgcolor=PLOT_BGCOLOR,
                                paper_bgcolor=PAPER_BGCOLOR,
                                font_color=FONT_COLOR,
                                xaxis=dict(showgrid=False),
                                yaxis=dict(showgrid=False))
    
    
    return map_figure, mag_linechart, magType_histogram, magSource_histogram, f"{filtered_data_percentage:.2f}%"
    
if __name__ == '__main__':
    app.run_server(debug=False)