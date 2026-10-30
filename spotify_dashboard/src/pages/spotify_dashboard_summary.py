from datetime import timedelta
import dash
from dash import html, dcc, Input, Output, callback
import dash_daq as daq
import plotly.graph_objects as go

import src.dashboard_plots.dashboard_plots_summary as dbps
from src.dashboard_helpers.dashboard_components import create_header
from src.dashboard_helpers.dashboard_data import get_data_as_of_text, get_latest_played_at, load_listening_data

data = load_listening_data()
latest_played_at = get_latest_played_at(data)

layout = html.Div([
    create_header('Listening Behaviour - Summary', active_page='Summary', data_as_of_text=get_data_as_of_text(latest_played_at)),
    
    # Summary stats and controls section
    html.Div([
        # KPI cards (left side)
        html.Div([
        # Row 1: 4 KPI cards
        html.Div([
            # Card 1: Average Track Duration
            html.Div([
                html.Div('Avg. Track Duration', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='avg-track-duration-value', children='0:00', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 2: Number of Tracks Played
            html.Div([
                html.Div('Number of Tracks Played', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='num-tracks-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 3: Number of Unique Tracks Played
            html.Div([
                html.Div('Number of Unique Tracks Played', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='num-unique-tracks-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 4: Number of Unique Artists Played
            html.Div([
                html.Div('Number of Unique Artists Played', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='num-unique-artists-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '12px',
            'flex': '1 1 0',
            'minHeight': '0'
        }),
        
        # Row 2: 4 KPI cards
        html.Div([
            # Card 5: Average Time Played per Track
            html.Div([
                html.Div('Avg. Time Played per Track', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='avg-time-played-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 6: Completion Rate
            html.Div([
                html.Div('Completion Rate', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='completion-rate-value', children='0%', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 7: Average Track Popularity
            html.Div([
                html.Div('Avg. Track Popularity', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='avg-track-popularity-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            }),
            
            # Card 8: Average Artist Popularity
            html.Div([
                html.Div('Avg. Artist Popularity', style={
                    'color': 'darkgrey',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontSize': '12px',
                    'marginBottom': '8px',
                    'textAlign': 'center',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word'
                }),
                html.Div(id='avg-artist-popularity-value', children='0', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '700',
                    'fontSize': '24px',
                    'textAlign': 'center'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '15px 20px 22px 20px',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',
                'minWidth': '0'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '12px',
            'flex': '1 1 0',
            'minHeight': '0'
        })
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '12px',
            'flex': '1 1 0',
            'minHeight': '0',
            'minWidth': '0'
        }),
        
        # Controls (right side)
        html.Div([
            # Date filter
            html.Div([
                # Slider with date displays
                html.Div([
                    # Start date (left)
                    html.Span(id='start-date-display', children='', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontWeight': '600',
                        'fontSize': '16px',
                        'padding': '8px 16px',
                        'borderRadius': '8px',
                        'backgroundColor': 'rgb(55, 55, 55)',
                        'marginRight': '0px',
                        'marginBottom': '18px',
                        'whiteSpace': 'nowrap'
                    }),
                    # Slider
                    html.Div([
                        dcc.Slider(
                            id='date-offset-input',
                            min=1,
                            max=365,
                            step=1,
                            value=90,
                            reverse=True,
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={
                        'flex': '1',
                        'minWidth': '200px'
                    }),
                    # End date (right)
                    html.Span(id='end-date-display', children='', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontWeight': '600',
                        'fontSize': '16px',
                        'padding': '8px 16px',
                        'borderRadius': '8px',
                        'backgroundColor': 'rgb(55, 55, 55)',
                        'marginLeft': '0px',
                        'marginTop': '0px',
                        'marginBottom': '18px',
                        'whiteSpace': 'nowrap'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '0px',
                    
                }),
            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                #'padding': '12px',
                'paddingLeft': '12px',
                'paddingRight': '12px',
                'paddingTop': '12px',
                'paddingBottom': '6px',
                'background-color': 'black',
                'border-radius': '20px'
            }),
            
            # Combined Key Toggles
            html.Div([
                # Minutes Played / Songs Played toggle
                html.Div([
                    html.Span(['Minutes', html.Br(), 'Played'], style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '10px',
                        'marginRight': '0px',
                        'textAlign': 'center',
                        'lineHeight': '1.4'
                    }),
                    daq.BooleanSwitch(
                        id='kpi-toggle',
                        on=False,
                        color='#1DB954',
                        style={'marginTop': '0', 'marginBottom': '0', 'marginLeft': '12px', 'marginRight': '12px', 'flexShrink': '0'}
                    ),
                    html.Span(['Songs', html.Br(), 'Played'], style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '0px',
                        'marginRight': '10px',
                        'textAlign': 'center',
                        'lineHeight': '1.4'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': 'rgb(55,55,55)',
                    'borderRadius': '20px',
                    'padding': '8px 2px',
                    'flex': '1 1 auto',
                    'minWidth': 'max-content',
                    'boxSizing': 'border-box'
                }),
                
                # Daily / Monthly toggle
                html.Div([
                    html.Span('Monthly', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '10px',
                        'marginRight': '0px',
                        'whiteSpace': 'nowrap'
                    }),
                    daq.BooleanSwitch(
                        id='agg-level-toggle',
                        on=True,
                        color='#1DB954',
                        style={'marginTop': '0', 'marginBottom': '0', 'marginLeft': '12px', 'marginRight': '12px', 'flexShrink': '0'}
                    ),
                    html.Span('Daily', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '0px',
                        'marginRight': '10px',
                        'whiteSpace': 'nowrap'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': 'rgb(55,55,55)',
                    'borderRadius': '20px',
                    'padding': '8px 2px',
                    'flex': '1 1 auto',
                    'minWidth': 'max-content',
                    'boxSizing': 'border-box'
                }),
                
                # Genre / Overall toggle
                html.Div([
                    html.Span('Overall', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '10px',
                        'marginRight': '0px',
                        'whiteSpace': 'nowrap'
                    }),
                    daq.BooleanSwitch(
                        id='genre-toggle',
                        on=False,
                        color='#1DB954',
                        style={'marginTop': '0', 'marginBottom': '0', 'marginLeft': '12px', 'marginRight': '12px', 'flexShrink': '0'}
                    ),
                    html.Span('Genre', style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'marginLeft': '0px',
                        'marginRight': '10px',
                        'whiteSpace': 'nowrap'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'backgroundColor': 'rgb(55,55,55)',
                    'borderRadius': '20px',
                    'padding': '8px 2px',
                    'flex': '1 1 auto',
                    'minWidth': 'max-content',
                    'boxSizing': 'border-box'
                })
            ], style={
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '8px',
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'gap': '10px',
                'overflowX': 'auto'
            })
        ], style={
            'flex': '0.66 1 0',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '8px',
            'justifyContent': 'center',
            'minWidth': '0'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'flexWrap': 'wrap',
        'gap': '12px',
        'flex': '0 1 auto'
    }),
    
    # Main content area with charts and Top 5 panels
    html.Div([
        # Left side: Two charts stacked vertically
        html.Div([
            # Time-series chart
            html.Div([
                dcc.Graph(
                    id='main-timeseries-chart',
                    figure={},
                    config={'responsive': True},
                    style={
                        'flex': '1 1 0',
                        'minHeight': '0',
                        'minWidth': '0',
                        'height': '100%',
                        'width': '100%'
                    }
                )
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '6px',
                'minHeight': '0',
                'minWidth': '0',
                'display': 'flex',
                'overflow': 'hidden'
            }),
            
            # Genre distribution chart
            html.Div([
                dcc.Graph(
                    id='genre-distribution-chart',
                    figure={},
                    config={'responsive': True},
                    style={
                        'flex': '1 1 0',
                        'minHeight': '0',
                        'minWidth': '0',
                        'height': '100%',
                        'width': '100%'
                    }
                )
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '6px',
                'minHeight': '0',
                'display': 'flex',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '1 1 0',
            'display': 'flex',
            'flexDirection': 'column',
            'gap': '12px',
            'minHeight': '0',
            'minWidth': '0'
        }),
        
        # Right side: Top 5 panels side by side
        html.Div([
            # Top 5 Most Played Songs
            html.Div([
                html.Div('Top 5 Most Played Songs', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '600',
                    'fontSize': '18px',
                    'marginBottom': '12px',
                    'textAlign': 'center'
                }),
                html.Div(id='top5-songs-panel', children=[], style={
                    'flex': '1 1 0',
                    'minHeight': '0',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '8px'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '12px',
                'minHeight': '0',
                'display': 'flex',
                'flexDirection': 'column',
                'overflow': 'hidden'
            }),
            
            # Top 5 Most Played Artists
            html.Div([
                html.Div('Top 5 Most Played Artists', style={
                    'color': 'white',
                    'fontFamily': 'Metropolis, sans-serif',
                    'fontWeight': '600',
                    'fontSize': '18px',
                    'marginBottom': '12px',
                    'textAlign': 'center'
                }),
                html.Div(id='top5-artists-panel', children=[], style={
                    'flex': '1 1 0',
                    'minHeight': '0',
                    'overflow': 'hidden',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '8px'
                })
            ], style={
                'flex': '1 1 0',
                'background-color': 'black',
                'border-radius': '20px',
                'padding': '12px',
                'minHeight': '0',
                'display': 'flex',
                'flexDirection': 'column',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '0.66 1 0',
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '12px',
            'minHeight': '0',
            'minWidth': '0'
        })
    ], style={
        'flex': '1 1 0',
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '12px',
        'minHeight': '0'
    })
    
], style={
    'height': '100vh',
    'width': '100%',
    'display': 'flex',
    'flexDirection': 'column',
    'backgroundColor': 'rgb(45, 45, 45)',
    'gap': '12px',
    'padding': '12px',
    'overflow': 'hidden',
    'boxSizing': 'border-box',
})

# Registered after the layout exists because pages_folder='' disables Dash's layout auto-import
dash.register_page(__name__, path='/', title='Listening Behaviour - Summary', layout=layout)


# Callback to update all components
@callback(
    [
        Output('start-date-display', 'children'),
        Output('end-date-display', 'children'),
        Output('avg-track-duration-value', 'children'),
        Output('num-tracks-value', 'children'),
        Output('num-unique-tracks-value', 'children'),
        Output('num-unique-artists-value', 'children'),
        Output('avg-time-played-value', 'children'),
        Output('completion-rate-value', 'children'),
        Output('avg-track-popularity-value', 'children'),
        Output('avg-artist-popularity-value', 'children'),
        Output('main-timeseries-chart', 'figure'),
        Output('genre-distribution-chart', 'figure'),
        Output('top5-songs-panel', 'children'),
        Output('top5-artists-panel', 'children')
    ],
    [
        Input('date-offset-input', 'value'),
        Input('kpi-toggle', 'on'),
        Input('agg-level-toggle', 'on'),
        Input('genre-toggle', 'on')
    ]
)
def update_dashboard(date_offset, kpi_on, agg_level_daily, genre_enabled):
    kpi = 'num_songs_played' if kpi_on else 'track_time_played_mins'
    # Calculate cutoff date
    today = latest_played_at
    cutoff_date = today - timedelta(days=date_offset)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
    
    # Format dates for display
    start_date_display = cutoff_date.strftime('%d.%m.%Y')
    end_date_display = today.strftime('%d.%m.%Y')
    delta_display = str(date_offset)
    
    # Get summary stats
    stats = dbps.create_summary_stats(data=data, cutoff_date=cutoff_date_str)
    
    # Format summary stats
    avg_duration_mins = int(stats['avg_track_duration_sec'] // 60)
    avg_duration_secs = int(stats['avg_track_duration_sec'] % 60)
    avg_track_duration_formatted = f"{avg_duration_mins}:{avg_duration_secs:02d}"
    
    num_tracks = f"{stats['n_songs_played']:,}"
    num_unique_tracks = f"{stats['n_unique_songs_played']:,}"
    num_unique_artists = f"{stats['n_unique_artists_played']:,}"
    
    avg_time_played_min = int(stats['avg_track_time_played_sec'] // 60)
    avg_time_played_secs = int(stats['avg_track_time_played_sec'] % 60)
    avg_time_played_formatted = f"{avg_time_played_min}:{avg_time_played_secs:02d}"
    
    completion_rate = f"{stats['completion_rate'] * 100:.1f}%"
    avg_track_popularity = f"{stats['avg_track_popularity']:.1f}%"
    avg_artist_popularity = f"{stats['avg_artist_popularity']:.1f}%"
    
    # Generate main time-series chart
    if genre_enabled:
        main_chart = dbps.listening_summary_stacked_bar_chart_genre(
            data=data,
            cutoff_date=cutoff_date_str,
            agg_level_daily=agg_level_daily,
            kpi=kpi
        )
    else:
        main_chart = dbps.listening_summary_bar_chart_overall(
            data=data,
            cutoff_date=cutoff_date_str,
            agg_level_daily=agg_level_daily,
            kpi=kpi
        )
    
    # Generate genre distribution chart
    genre_chart = dbps.listening_summary_genre_chart_overall(
        data=data,
        cutoff_date=cutoff_date_str,
        kpi=kpi
    )
    
    # Generate Top 5 data
    top5_tracks_df = dbps.create_top5_input_data(
        data=data,
        cutoff_date=cutoff_date_str,
        tracks=True,
        sort_by_track_time=True
    )
    
    top5_artists_df = dbps.create_top5_input_data(
        data=data,
        cutoff_date=cutoff_date_str,
        tracks=False,
        sort_by_track_time=True
    )
    
    # Build Top 5 Songs panel
    top5_songs_components = []
    for idx, row in top5_tracks_df.iterrows():
        song_component = html.Div([
            html.Div([
                html.Img(
                    src=row['album_image_url'],
                    style={
                        'height': '100%',
                        'width': 'auto',
                        'aspectRatio': '1/1',
                        'maxHeight': '80px',
                        'borderRadius': '8px',
                        'objectFit': 'cover',
                        'marginRight': '16px',
                        'flex': '0 0 auto'
                    }
                ),
                html.Div([
                    html.Div(row['track_name'], style={
                        'color': 'white',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'marginBottom': '4px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'whiteSpace': 'nowrap'
                    }),
                    html.Div(row['first_artist_name'], style={
                        'color': 'darkgrey',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '14px',
                        'marginBottom': '4px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'whiteSpace': 'nowrap'
                    }),
                    html.Div(f"{int(row['track_time_played'] / 60)} mins • {row['track_count_played']} plays", style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '13px'
                    })
                ], style={
                    'flex': '1 1 0',
                    'minWidth': '0',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'padding': '12px',
                'backgroundColor': 'rgb(30, 30, 30)',
                'borderRadius': '12px',
                'flex': '1 1 0',
                'minHeight': '0',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '1 1 0',
            'minHeight': '0',
            'display': 'flex',
            'flexDirection': 'column'
        })
        top5_songs_components.append(song_component)
    
    # Build Top 5 Artists panel
    top5_artists_components = []
    for idx, row in top5_artists_df.iterrows():
        artist_component = html.Div([
            html.Div([
                html.Img(
                    src=row['artist_image_url'],
                    style={
                        'height': '100%',
                        'width': 'auto',
                        'aspectRatio': '1/1',
                        'maxHeight': '80px',
                        'borderRadius': '50%',
                        'objectFit': 'cover',
                        'marginRight': '16px',
                        'flex': '0 0 auto'
                    }
                ),
                html.Div([
                    html.Div(row['first_artist_name'], style={
                        'color': 'white',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'marginBottom': '6px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'whiteSpace': 'nowrap'
                    }),
                    html.Div(f"{int(row['track_time_played'] / 60)} mins • {row['track_count_played']} plays", style={
                        'color': 'rgb(40, 210, 100)',
                        'fontFamily': 'Metropolis, sans-serif',
                        'fontSize': '13px'
                    })
                ], style={
                    'flex': '1 1 0',
                    'minWidth': '0',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center'
                })
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'padding': '12px',
                'backgroundColor': 'rgb(30, 30, 30)',
                'borderRadius': '12px',
                'flex': '1 1 0',
                'minHeight': '0',
                'overflow': 'hidden'
            })
        ], style={
            'flex': '1 1 0',
            'minHeight': '0',
            'display': 'flex',
            'flexDirection': 'column'
        })
        top5_artists_components.append(artist_component)
    
    return (
        start_date_display,
        end_date_display,
        avg_track_duration_formatted,
        num_tracks,
        num_unique_tracks,
        num_unique_artists,
        avg_time_played_formatted,
        completion_rate,
        avg_track_popularity,
        avg_artist_popularity,
        main_chart,
        genre_chart,
        top5_songs_components,
        top5_artists_components
    )
