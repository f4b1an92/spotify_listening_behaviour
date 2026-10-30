import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

import src.dashboard_plots.dashboard_plots_comparison as dbp
from src.dashboard_helpers.dashboard_components import create_header
from src.dashboard_helpers.dashboard_data import get_data_as_of_text, get_latest_played_at, load_listening_data

# Keep only rows with audio features (new frame, the shared data stays untouched)
data = load_listening_data()
latest_played_at = get_latest_played_at(data)
data = data.loc[~data['acousticness'].isnull(), :].reset_index(drop=True)

layout = html.Div([
    create_header('Listening Behaviour - Compare', active_page='Compare', data_as_of_text=get_data_as_of_text(latest_played_at)),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='main-song-input',
                options=[{'label': track, 'value': track} for track in data['track_name'].unique()],
                value='',
                placeholder='Enter Main Song Name',
                searchable=True,
                clearable=True,
                className='main-dropdown',
                style={'width': '100%'}
            ),
        ], style={'flex': '1 1 0', 'minWidth': '0'}),
        html.Div(style={'flex': '1 1 0', 'minWidth': '0'}),  # Spacer to match the center polar charts
        html.Div([
            dcc.Dropdown(
                id='reference-song-input',
                options=[{'label': track, 'value': track} for track in data['track_name'].unique()],
                value='',
                placeholder='Enter Reference Song Name',
                searchable=True,
                clearable=True,
                className='reference-dropdown',
                style={'width': '100%'}
            ),
        ], style={'flex': '1 1 0', 'minWidth': '0'}),
    ], style={
        'width': '100%', 'margin': '0', 'minWidth': '0',
        'border-radius': '20px', 'background-color': 'black',
        'padding': '12px',
        'display': 'flex', 'flexDirection': 'row', 'alignItems': 'stretch', 'gap': '12px',
        'flex': '0 0 auto',
        'position': 'relative', 'zIndex': '10'  # Keeps the open dropdown menus above the charts
    }),

    # Upper section with images and polar charts
    html.Div([
        # Left side: 2 images stacked
        html.Div([
            html.Div([
                html.Img(id='album-image-left', src='', style={
                    'width': '31%', 'height': '94%', 'border': '2px solid rgb(40, 210, 100)',
                    'border-radius': '20px', 'padding': '4px', 'flexShrink': '0'
                }),
                html.Div([ # Song info box
                    html.Div([ # NEW LAYER - Track Name
                        html.Div(
                            #id='song-text-box-left-categories',
                            id='song-text-box-left-track-name-category',
                            children=[
                                'Track Name:', #html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-left-data',
                            id='song-text-box-left-track-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Track Length
                        html.Div(
                            #id='song-text-box-left-categories',
                            id='song-text-box-left-track-length-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                'Track Length:', #html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-left-data',
                            id='song-text-box-left-track-length-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Album Name
                        html.Div(
                            #id='song-text-box-left-categories',
                            id='song-text-box-left-album-name-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                'Album Name:', #html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-left-data',
                            id='song-text-box-left-album-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px','background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Track Popularity
                        html.Div(
                            #id='song-text-box-left-categories',
                            id='song-text-box-left-track-popularity-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-left-data',
                            id='song-text-box-left-track-popularity-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                ], style={
                    'flex': '1 1 0', 'height': '100%', 'minWidth': '0',
                    'padding': '6px', 'maxWidth': '100%',
                    'font-size': '14px', 'color': 'white', 'align-items': 'top', 'margin-left': '0px',
                    'display': 'flex', 'flexDirection': 'column', 'gap': '6px', 'minHeight': '0',
                    'overflow': 'hidden'
                })
            ], style={
                'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'background-color': 'black',
                'border-radius': '20px', 'padding': '8px',
                'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '4px',
                'overflow': 'hidden'
            }),
            html.Div([
                html.Img(id='artist-image-left', src='', style={
                    'width': '31%', 'height': '94%', 'border': '2px solid rgb(40, 210, 100)',
                    'border-radius': '20px', 'padding': '4px', 'flexShrink': '0'
                }),
                html.Div([ # Artist info box
                    html.Div([ # NEW LAYER - Artist Name
                        html.Div(
                            #id='artist-text-box-left-categories',
                            id='artist-text-box-left-artist-name-category',
                            children=[
                                'Artist Name:', #html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-left-data',
                            id='artist-text-box-left-artist-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Genre
                        html.Div(
                            #id='artist-text-box-left-categories',
                            id='artist-text-box-left-genre-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                'Genre:', #html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-left-data',
                            id='artist-text-box-left-genre-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Artist Followers
                        html.Div(
                            #id='artist-text-box-left-categories',
                            id='artist-text-box-left-artist-followers-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                'Artist Followers:', #html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-left-data',
                            id='artist-text-box-left-artist-followers-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Artist Popularity
                        html.Div(
                            #id='artist-text-box-left-categories',
                            id='artist-text-box-left-artist-popularity-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                'Artist Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-left-data',
                            id='artist-text-box-left-artist-popularity-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(40, 210, 100)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                ], style={
                    'flex': '1 1 0', 'height': '100%', 'minWidth': '0',
                    'padding': '6px', 'maxWidth': '100%',
                    'font-size': '14px', 'color': 'white', 'align-items': 'top',
                    'display': 'flex', 'flexDirection': 'column', 'gap': '6px', 'minHeight': '0',
                    'overflow': 'hidden'
                })
            ], style={
                'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'background-color': 'black',
                'border-radius': '20px', 'padding': '8px',
                'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '4px',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
            'display': 'flex', 'flexDirection': 'column', 'gap': '12px',
            'overflow': 'hidden'
        }),
        
        # Center plots (wrapped in panels)
        # Center plots (wrapped in panels)
        html.Div([
            html.Div(
                id='spotify-polar-chart-upper-left-title',
                children=['Loudness in Decibels'],
                style={
                    'width': '96.5%', 'text-align': 'center',
                    'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600', 'fontSize': '18px',
                    'color': 'black', 'background-color': 'darkgrey',
                    'border-radius': '12px', 'margin': '0 0 6px 0',
                    'padding': '6px'
                }
            )
            , dcc.Graph(id='spotify-polar-chart-upper-left', figure={}, style={'flex': '1 1 0', 'minHeight': '0'})
        ], style={
            'flex': '0.6 1 0',
            'minHeight': '0',
            'minWidth': '0',
            'background-color': 'black',
            'border-radius': '20px',
            'padding': '6px',
            'display': 'flex',
            'flexDirection': 'column',
            'overflow': 'hidden'
        }),
        html.Div([
            html.Div(
                id='spotify-polar-chart-upper-right-title',
                children=['Tempo in Beats per Minute'],
                style={
                    'width': '96.5%', 'text-align': 'center',
                    'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600', 'fontSize': '18px',
                    'color': 'black', 'background-color': 'darkgrey',
                    'border-radius': '12px', 'margin': '0 0 6px 0',
                    'padding': '6px'
                }
            )
            , dcc.Graph(id='spotify-polar-chart-upper-right', figure={}, style={'flex': '1 1 0', 'minHeight': '0'})
        ], style={
            'flex': '0.6 1 0',
            'minHeight': '0',
            'minWidth': '0',
            'background-color': 'black',
            'border-radius': '20px',
            'padding': '6px',
            'display': 'flex',
            'flexDirection': 'column',
            'overflow': 'hidden'
        }),
        
        # Right side: 2 images stacked
        html.Div([
            html.Div([ # Song section (image + info)
                html.Div([ # Song info box
                    html.Div([ # NEW LAYER - Track Name
                        html.Div(
                            #id='song-text-box-right-categories',
                            id='song-text-box-right-track-name-category',
                            children=[
                                'Track Name:', #html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-right-data',
                            id='song-text-box-right-track-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Track Length
                        html.Div(
                            #id='song-text-box-right-categories',
                            id='song-text-box-right-track-length-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                'Track Length:', #html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-right-data',
                            id='song-text-box-right-track-length-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Album Name
                        html.Div(
                            #id='song-text-box-right-categories',
                            id='song-text-box-right-album-name-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                'Album Name:', #html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-right-data',
                            id='song-text-box-right-album-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Track Popularity
                        html.Div(
                            #id='song-text-box-right-categories',
                            id='song-text-box-right-track-popularity-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='song-text-box-right-data',
                            id='song-text-box-right-track-popularity-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                ], style={
                    'flex': '1 1 0', 'height': '100%', 'minWidth': '0',
                    'padding': '6px', 'maxWidth': '100%',
                    'font-size': '14px', 'color': 'white', 'align-items': 'top',
                    'display': 'flex', 'flexDirection': 'column', 'gap': '6px', 'minHeight': '0',
                    'overflow': 'hidden'
                }),
                html.Img(id='album-image-right', src='', style={
                    'width': '31%', 'height': '94%', 'border': '2px solid rgb(0, 191, 255)',
                    'border-radius': '20px', 'padding': '4px', 'flexShrink': '0'
                }),
            ], style={
                'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'background-color': 'black',
                'border-radius': '20px', 'padding': '8px',
                'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '4px',
                'overflow': 'hidden'
            }),
            html.Div([ # Artist section (image + info)
                html.Div([ # Artist info box
                    html.Div([ # NEW LAYER - Artist Name
                        html.Div(
                            #id='artist-text-box-right-categories',
                            id='artist-text-box-right-artist-name-category',
                            children=[
                                'Artist Name:', #html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-right-data',
                            id='artist-text-box-right-artist-name-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Genre
                        html.Div(
                            #id='artist-text-box-right-categories',
                            id='artist-text-box-right-genre-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                'Genre:', #html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-right-data',
                            id='artist-text-box-right-genre-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Artist Followers
                        html.Div(
                            #id='artist-text-box-right-categories',
                            id='artist-text-box-right-artist-followers-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                'Artist Followers:', #html.Br(), html.Br(),
                                #'Track Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-right-data',
                            id='artist-text-box-right-artist-followers-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                    html.Div([ # NEW LAYER - Artist Popularity
                        html.Div(
                            #id='artist-text-box-right-categories',
                            id='artist-text-box-right-artist-popularity-category',
                            children=[
                                #'Track Name:', html.Br(), html.Br(),
                                #'Track Length:', html.Br(), html.Br(),
                                #'Album Name:', html.Br(), html.Br(),
                                'Artist Popularity:'
                            ],
                            style={
                                'width': '45%', 'height': '100%', 'text-align': 'left',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center', 'lineHeight': '1.1'
                            }
                        ),
                        html.Div(
                            #id='artist-text-box-right-data',
                            id='artist-text-box-right-artist-popularity-data',
                            children=[],
                            style={
                                'width': '55%', 'height': '100%', 'text-align': 'right',
                                'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
                                'color': 'black', 'overflow': 'hidden',
                                'white-space': 'nowrap', 'text-overflow': 'ellipsis',
                                'display': 'flex', 'alignItems': 'center',
                                'justifyContent': 'flex-end', 'lineHeight': '1.1'
                            }
                        ),
                    ], style={
                        'display': 'flex', 'justify-content': 'space-between',
                        'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
                        'border-radius': '10px', 'background-color': 'rgb(0, 191, 255)',
                        'padding': '6px 8px', 'gap': '8px', 'alignItems': 'center',
                        'overflow': 'hidden'
                    }), # NEW LAYER END
                ], style={
                    'flex': '1 1 0', 'height': '100%', 'minWidth': '0',
                    'padding': '6px', 'maxWidth': '100%',
                    'font-size': '14px', 'color': 'white', 'align-items': 'top',
                    'display': 'flex', 'flexDirection': 'column', 'gap': '6px', 'minHeight': '0',
                    'overflow': 'hidden'
                }),
                html.Img(id='artist-image-right', src='', style={
                    'width': '31%', 'height': '94%', 'border': '2px solid rgb(0, 191, 255)',
                    'border-radius': '20px', 'padding': '4px', 'flexShrink': '0'
                }),
            ], style={
                'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'background-color': 'black',
                'border-radius': '20px', 'padding': '8px',
                'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '4px',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0', 'alignSelf': 'stretch',
            'display': 'flex', 'flexDirection': 'column', 'gap': '12px',
            'overflow': 'hidden'
        }),
    ], style={
        'display': 'flex', 'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0',
        'width': '100%', 'maxWidth': '100%',
        'justifyContent': 'stretch', 'alignItems': 'stretch', 'gap': '12px',
        'overflow': 'hidden'
    }),
    html.Div([
        html.Div([
            dcc.Graph(id='spotify-bar-chart-lower-left', figure={}, style={
                'width': '100%',
                'height': '100%'
            })
        ], style={
            'flex': '1 1 0',
            'minHeight': '0',
            'minWidth': '0',
            'background-color': 'black',
            'border-radius': '20px',
            'padding': '6px',
            'overflow': 'hidden'
        }),
        html.Div([
            dcc.Graph(id='spotify-radar-chart-lower-center', figure={}, style={
                'width': '100%',
                'height': '100%'
            })
        ], style={
            'flex': '1 1 0',
            'minHeight': '0',
            'minWidth': '0',
            'background-color': 'black',
            'border-radius': '20px',
            'padding': '6px',
            'overflow': 'hidden'
        }),
        html.Div([
            dcc.Graph(id='spotify-bar-chart-lower-right', figure={}, style={
                'width': '100%',
                'height': '100%'
            })
        ], style={
            'flex': '1 1 0',
            'minHeight': '0',
            'minWidth': '0',
            'background-color': 'black',
            'border-radius': '20px',
            'padding': '6px',
            'overflow': 'hidden'
        })
    ], style={
        'display': 'flex', 'flex': '1 1 0', 'minHeight': '0', 'minWidth': '0',
        'width': '100%', 'maxWidth': '100%',
        'justifyContent': 'stretch', 'gap': '12px',
        'overflow': 'hidden'
    }),
], style={
    'text-align': 'center', 
    'height': '100vh',
    'width': '100%',
    'maxWidth': '100vw',
    'overflow': 'hidden',
    'background-color': 'rgb(45, 45, 45)', 
    'padding': '12px',
    'margin': '0px',
    'display': 'flex',
    'flexDirection': 'column',
    'gap': '12px',
    'boxSizing': 'border-box'
})

# Registered after the layout exists because pages_folder='' disables Dash's layout auto-import
dash.register_page(__name__, path='/compare', title='Listening Behaviour - Compare', layout=layout)


# Callback function to update graph and average happiness div
@callback(
    [
        Output(component_id='artist-image-left', component_property='src'),
        Output(component_id='album-image-left', component_property='src'),
        Output(component_id='artist-image-right', component_property='src'),
        Output(component_id='album-image-right', component_property='src'),
        #Output(component_id='song-text-box-left-data', component_property='children'),
        Output(component_id='song-text-box-left-track-name-data', component_property='children'),
        Output(component_id='song-text-box-left-track-length-data', component_property='children'),
        Output(component_id='song-text-box-left-album-name-data', component_property='children'),
        Output(component_id='song-text-box-left-track-popularity-data', component_property='children'),
        #Output(component_id='artist-text-box-left-data', component_property='children'),
        Output(component_id='artist-text-box-left-artist-name-data', component_property='children'),
        Output(component_id='artist-text-box-left-genre-data', component_property='children'),
        Output(component_id='artist-text-box-left-artist-followers-data', component_property='children'),
        Output(component_id='artist-text-box-left-artist-popularity-data', component_property='children'),
        #Output(component_id='song-text-box-right-data', component_property='children'),
        Output(component_id='song-text-box-right-track-name-data', component_property='children'),
        Output(component_id='song-text-box-right-track-length-data', component_property='children'),
        Output(component_id='song-text-box-right-album-name-data', component_property='children'),
        Output(component_id='song-text-box-right-track-popularity-data', component_property='children'),
        #Output(component_id='artist-text-box-right-data', component_property='children'),
        Output(component_id='artist-text-box-right-artist-name-data', component_property='children'),
        Output(component_id='artist-text-box-right-genre-data', component_property='children'),
        Output(component_id='artist-text-box-right-artist-followers-data', component_property='children'),
        Output(component_id='artist-text-box-right-artist-popularity-data', component_property='children'),

        Output(component_id='spotify-polar-chart-upper-left', component_property='figure'),
        Output(component_id='spotify-polar-chart-upper-right', component_property='figure'),
        Output(component_id='spotify-bar-chart-lower-left', component_property='figure'),
        Output(component_id='spotify-radar-chart-lower-center', component_property='figure'),
        Output(component_id='spotify-bar-chart-lower-right', component_property='figure')
    ],
    #Input(component_id='submit-button', component_property='n_clicks'), # component_property of Input is what's handed over to the function. In this case, it merely triggers the update of the figure
    #State(component_id='main-song-input', component_property='value'),  # component_property of State is what's handed over to the function IF the button is clicked which is the only trigger for the update function
    #State(component_id='reference-song-input', component_property='value')  # component_property of State is what's handed over to the function IF the button is clicked which is the only trigger for the update function
    Input(component_id='main-song-input', component_property='value'),  # component_property of State is what's handed over to the function IF the button is clicked which is the only trigger for the update function
    Input(component_id='reference-song-input', component_property='value')  # component_property of State is what's handed over to the function IF the button is clicked which is the only trigger for the update function

)
def update_figure(main_song, reference_song): # n_clicks is required to trigger the update when button is clicked even though it is not used in the function
    if (main_song == '') & (reference_song == ''):
        idx_main = 0
        idx_ref = 1
    elif (main_song == '') & (reference_song != ''):
        idx_main = 0
        idx_ref = data.loc[data['track_name'] == reference_song, :].index[0]
    elif (main_song != '') & (reference_song == ''):
        idx_main = data.loc[data['track_name'] == main_song, :].index[0]
        idx_ref = 1
    else:
        idx_main = data.loc[data['track_name'] == main_song, :].index[0]
        idx_ref = data.loc[data['track_name'] == reference_song, :].index[0]
    
    # Get image URLs from data
    artist_image_left = data.loc[idx_main, 'artist_image_url']
    album_image_left = data.loc[idx_main, 'album_image_url']
    artist_image_right = data.loc[idx_ref, 'artist_image_url']
    album_image_right = data.loc[idx_ref, 'album_image_url']

    # Figures at top
    fig_center_left = dbp.song_comparison_polar_chart(data=data, feature_name='loudness', idx_main=idx_main, idx_ref=idx_ref)
    fig_center_right = dbp.song_comparison_polar_chart(data=data, feature_name='tempo', idx_main=idx_main, idx_ref=idx_ref)
    
    # Figures at bottom
    fig_left = dbp.song_comparison_audio_feature_bar_chart(data=data, track_idx=idx_main, track_type='main')
    fig_middle = dbp.song_comparison_radar_chart(data=data, idx_main=idx_main, idx_ref=idx_ref)
    fig_right = dbp.song_comparison_audio_feature_bar_chart(data=data, track_idx=idx_ref, track_type='ref')

    # Text for first text box (left side)
    left_text_box_song = [
        f'{data.loc[idx_main, "track_name"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "track_duration_min_sec"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "album_name"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "track_popularity"]:,.0f}',
    ]
    left_text_box_artist = [
        f'{data.loc[idx_main, "combined_artist_names"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "main_genre"].capitalize()}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "artist_followers_total"]:,.0f}', #html.Br(), html.Br(),
        f'{data.loc[idx_main, "artist_popularity"]:,.0f}' 
    ]

    # Text for first text box (left side)
    right_text_box_song = [
        f'{data.loc[idx_ref, "track_name"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "track_duration_min_sec"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "album_name"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "track_popularity"]:,.0f}',
    ]
    right_text_box_artist = [
        f'{data.loc[idx_ref, "combined_artist_names"]}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "main_genre"].capitalize()}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "artist_followers_total"]:,.0f}', #html.Br(), html.Br(),
        f'{data.loc[idx_ref, "artist_popularity"]:,.0f}',
    ]
    
    return (
        artist_image_left, album_image_left, artist_image_right, album_image_right, 
        left_text_box_song[0], left_text_box_song[1], left_text_box_song[2], left_text_box_song[3], 
        left_text_box_artist[0], left_text_box_artist[1], left_text_box_artist[2], left_text_box_artist[3], 
        right_text_box_song[0], right_text_box_song[1], right_text_box_song[2], right_text_box_song[3],
        right_text_box_artist[0], right_text_box_artist[1], right_text_box_artist[2], right_text_box_artist[3],  
        fig_center_left, fig_center_right, 
        fig_left, fig_middle, fig_right
    )
