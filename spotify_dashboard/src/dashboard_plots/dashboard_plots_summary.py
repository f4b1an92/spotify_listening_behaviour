import os
import sys
import re
from typing import Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go


def listening_summary_bar_chart_overall(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp], agg_level_daily: bool = True,
                                        kpi: str = 'track_time_played_mins') -> go.Figure:
    """"""
    # Check that kpi is valid
    valid_kpis = ['track_time_played_mins', 'num_songs_played']
    if kpi == 'track_time_played_mins':
        title_label = 'Listening Time'
        dim_label='Time'
        dim_unit = '(mins.)'
        dim_unit_hover = re.sub(r'\(|\)', '', dim_unit)
        hover_decimaul_places = 1
    elif kpi == 'num_songs_played':
        title_label = 'Songs Played'
        dim_label='Songs'
        dim_unit = ''
        dim_unit_hover = ''
        hover_decimaul_places = 0
    else:
        raise ValueError(f"Invalid kpi: {kpi}. Valid options are: {valid_kpis}")

    # Create variable that indicates that stores labels to get correct agg_level keys
    if agg_level_daily:
        agg_df_key = 'df_agg_daily_overall'
        agg_level = 'played_at_date'
        agg_label = 'Date'
    else:
        agg_df_key = 'df_agg_monthly_overall'
        agg_level = 'played_at_month'
        agg_label = 'Month'

    # Create actual input dataframe for plotting
    input_data_dict = _create_input_data_summary_sheet_plots(data=data, cutoff_date=cutoff_date)

    # Create actual plot
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=input_data_dict[agg_df_key][agg_level], 
        y=input_data_dict[agg_df_key][kpi], 
        marker=dict(color='rgb(30, 215, 96)'),
        name=title_label,
        hovertemplate=f"<b>{dim_label} Played:</b> %{{y:.{hover_decimaul_places}f}} {dim_unit_hover}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        autosize=True,
        title=title_label,
        #xaxis_title=agg_label,
        yaxis_title=f'{dim_label} Played {dim_unit}',
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', size=14, family='Metropolis, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True
        ),
        hovermode='x unified',
        margin=dict(t=50, l=50, r=50, b=50)  # Add margins
    )

    return fig

def listening_summary_stacked_bar_chart_genre(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp], agg_level_daily: bool = True, 
                                              kpi: str = 'track_time_played_mins') -> go.Figure:
    """"""
    # Check that kpi is valid
    valid_kpis = ['track_time_played_mins', 'num_songs_played']
    if kpi == 'track_time_played_mins':
        title_label = 'Listening Time'
        dim_label='Time'
        dim_unit = '(mins.)'
        dim_unit_hover = re.sub(r'\(|\)', '', dim_unit)
        hover_decimaul_places = 1
    elif kpi == 'num_songs_played':
        title_label = 'Songs Played'
        dim_label='Songs'
        dim_unit = ''
        dim_unit_hover = ''
        hover_decimaul_places = 0
    else:
        raise ValueError(f"Invalid kpi: {kpi}. Valid options are: {valid_kpis}")

    # Create actual input dataframe for plotting
    input_data_dict = _create_input_data_summary_sheet_plots(data=data, cutoff_date=cutoff_date)
    
    # Create variables that define agg-dimension specific data & labels for plotting
    if agg_level_daily:
        df_agg_genre = input_data_dict['df_agg_daily_genre'].copy()
        agg_level = 'played_at_date'
        agg_label = 'Date'
    else:
        df_agg_genre = input_data_dict['df_agg_monthly_genre'].copy()
        agg_level = 'played_at_month'
        agg_label = 'Month'
    
    # Create the figure
    fig = go.Figure()

    # Create properly sorted genre_df for use in summary sheet plots
    genre_df = input_data_dict['df_agg_genre_overall'].copy()

    genre_df = pd.concat([
        genre_df.loc[genre_df['top10_genres']!='Others'].sort_values(by=kpi, ascending=False),
        genre_df.loc[genre_df['top10_genres']=='Others']
    ],axis=0).reset_index(drop=True)

    # Get unique genres in correct order for color assignment in plots
    genres = genre_df['top10_genres'].unique()

    # Define a color palette for genres (you can customize these)
    color_list = [
        'rgb(0, 230, 118)', # Neon green
        'rgb(54, 162, 235)', # Bright blue
        'rgb(231, 76, 60)', # Red
        'rgb(135, 206, 250)', # Light blue
        'rgb(255, 105, 180)', # Hot pink
        'rgb(99, 110, 114)', # Dark gray
        'rgb(255, 235, 59)', # Peach
        'rgb(108, 92, 231)', # Blue-purple
        'rgb(255, 159, 64)', # Orange
        'rgb(169, 169, 169)' # Light gray
    ]
    color_mapping = {genre: color for genre, color in zip(genres, color_list)}

    # Add a trace for each genre
    for genre in genres:
        input_df_genre = df_agg_genre[df_agg_genre['top10_genres'] == genre]
        
        fig.add_trace(go.Bar(
            x=input_df_genre[agg_level],
            y=input_df_genre[kpi],
            name=genre,
            marker=dict(color=color_mapping.get(genre, 'rgb(30, 215, 96)')),
            hovertemplate=f'<b>Genre:</b> {genre}<br><b>Date:</b> %{{x}}<br><b>{dim_label}:</b> %{{y:.{hover_decimaul_places}f}} {dim_unit_hover}<br>──────────<extra></extra>'
        ))

    # Update layout
    fig.update_layout(
        autosize=True,
        barmode='stack',
        title=f'{title_label} by Genre',
        xaxis_title=agg_label,
        yaxis_title=f'{dim_label} Played {dim_unit}',
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', size=14, family='Metropolis, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True
        ),
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.5)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white', size=12, family='Metropolis, sans-serif'),
        ),
        margin=dict(t=50, l=50, r=50, b=50)  # Add margins
    )

    return fig

def listening_summary_genre_chart_overall(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp], 
                                          kpi: str = 'track_time_played_mins') -> go.Figure:
    """"""
    # Check that kpi is valid
    valid_kpis = ['track_time_played_mins', 'num_songs_played']
    if kpi == 'track_time_played_mins':
        title_label = 'Listening Time'
        dim_unit = '(mins.)'
        dim_unit_hover = re.sub(r'\(|\)', '', dim_unit)
        hover_decimaul_places = 0
    elif kpi == 'num_songs_played':
        title_label = 'Songs Played'
        dim_unit = ''
        dim_unit_hover = ''
        hover_decimaul_places = 0
    else:
        raise ValueError(f"Invalid kpi: {kpi}. Valid options are: {valid_kpis}")

    # Create actual input dataframe for plotting
    df_genre_overall = _create_input_data_summary_sheet_plots(data=data, cutoff_date=cutoff_date)['df_agg_genre_overall']
    
    # Sort by the selected KPI in descending order
    df_genre_overall = pd.concat([
        df_genre_overall.loc[df_genre_overall['top10_genres']!='Others'].sort_values(by=kpi, ascending=False),
        df_genre_overall.loc[df_genre_overall['top10_genres']=='Others'],
    ],axis=0).reset_index(drop=True)

    # Create colors list based on genres
    #colors = [color_palette.get(genre, 'rgb(30, 215, 96)') for genre in df_genre_overall['top10_genres']]
    colors = [
        'rgb(0, 230, 118)', # Neon green
        'rgb(54, 162, 235)', # Bright blue
        'rgb(231, 76, 60)', # Red
        'rgb(135, 206, 250)', # Light blue
        'rgb(255, 105, 180)', # Hot pink
        'rgb(99, 110, 114)', # Dark gray
        'rgb(255, 235, 59)', # Peach
        'rgb(108, 92, 231)', # Blue-purple
        'rgb(255, 159, 64)', # Orange
        'rgb(169, 169, 169)' # Light gray
    ]

    # Create the bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_genre_overall['top10_genres'],
        y=df_genre_overall[kpi],
        marker=dict(color=colors),
        text=[f'{val:.{hover_decimaul_places}f}' for val in df_genre_overall[kpi]],
        textposition='outside',
        cliponaxis=False,
        hovertemplate=f'<b>Genre:</b> %{{x}}<br><b>{title_label}:</b> %{{y:.{hover_decimaul_places}f}} {dim_unit_hover}<extra></extra>'
    ))

    # Calculate y-axis upper bound with padding for text labels
    y_max = df_genre_overall[kpi].max()
    y_upper = y_max * 1.15

    # Update layout
    fig.update_layout(
        autosize=True,
        title=f'Top 10 Genres by {title_label}',
        #xaxis_title='Genre',
        yaxis_title=f'{title_label} {dim_unit}',
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', size=14, family='Metropolis, sans-serif'),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            showgrid=True,
            range=[0, y_upper]
        ),
        showlegend=False,
        margin=dict(t=60, l=50, r=50, b=50)  # Add margins
    )

    return fig

def _create_input_data_summary_sheet_plots(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp]) -> dict:
    """"""
    data = data.copy()

    # Filter data based on cutoff_date. Only include songs played at or after the cutoff_date. Exclude songs 
    # with missing genre label.
    if isinstance(cutoff_date, str):
        cutoff_date = pd.to_datetime(cutoff_date)
    cond_date = pd.to_datetime(data['played_at']) >= cutoff_date
    cond_genre_unknown = data['simplified_main_genre'] != 'Unknown'

    # Create new column for top 10 genres (top 9 + "Others" category for all remaining genres).
    top9_genres = data.loc[cond_date & cond_genre_unknown, 'simplified_main_genre'].value_counts().head(9).index.tolist()
    data['top10_genres'] = data['simplified_main_genre'].apply(lambda x: x.capitalize() if x in top9_genres else 'Others')

    # Transform data in 'played_at' and 'track_time_played' cols. to create new features for aggregation
    data['played_at_date'] = pd.to_datetime(data['played_at']).dt.date
    data['played_at_month'] = pd.to_datetime(data['played_at']).dt.strftime('%Y-%m')
    data['track_time_played_mins'] = data['track_time_played'] / 60 # 'track_time_played' is in seconds

    # Create aggregated dataframes for daily and monthly time series plots
    agg_df_dict = {}
    agg_df_names = [
        'df_agg_daily_overall',
        'df_agg_monthly_overall',
        'df_agg_genre_overall',
        'df_agg_daily_genre',
        'df_agg_monthly_genre'
    ]
    agg_col_list = [
        ['played_at_date'],
        ['played_at_month'],
        ['top10_genres'],
        ['top10_genres', 'played_at_date'],
        ['top10_genres', 'played_at_month']
    ]

    for agg_name, agg_cols in zip(agg_df_names, agg_col_list):
        df_agg = data.loc[cond_date].groupby(agg_cols).agg({
            'track_id': 'count'
            , 'track_time_played_mins': 'sum'
        }).reset_index().rename(columns={
            'track_id': 'num_songs_played'
        })
        if (('played_at_date' in agg_cols) | ('played_at_month' in agg_cols)):
            df_agg = _fill_missing_played_at_dates(df_agg=df_agg)
        agg_df_dict[agg_name] = df_agg

    return agg_df_dict

def _fill_missing_played_at_dates(df_agg: pd.DataFrame) -> pd.DataFrame:
    if 'played_at_date' in df_agg.columns:    
        min_date = df_agg['played_at_date'].min()
        max_date = df_agg['played_at_date'].max()
        date_df = pd.DataFrame({'played_at_date': pd.date_range(start=min_date, end=max_date).date})
        df_agg = date_df.merge(df_agg, on='played_at_date', how='left').fillna(0)
    elif 'played_at_month' in df_agg.columns:
        min_date = pd.to_datetime(df_agg['played_at_month'].min())
        max_date = pd.to_datetime(df_agg['played_at_month'].max())
        date_df = pd.DataFrame({'played_at_month': pd.date_range(start=min_date, end=max_date).strftime('%Y-%m').unique()})
        df_agg = date_df.merge(df_agg, on='played_at_month', how='left').fillna(0)
    else:
        raise ValueError("Neither 'played_at_date' nor 'played_at_month' found in df_agg columns.")
    
    return df_agg

def create_top5_input_data(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp], tracks: bool = True,
                           sort_by_track_time: bool = True) -> pd.DataFrame:
    """"""
    if tracks:
        agg_col_list = ['track_name','first_artist_name', 'album_image_url']
    else:
        agg_col_list = ['first_artist_name','artist_image_url']

    if sort_by_track_time:
        sorting_dim = 'track_time_played'
    else:
        sorting_dim = 'track_count_played'

    # Top 5 (incl. image-url)
    if isinstance(cutoff_date, str):
        cutoff_date = pd.to_datetime(cutoff_date)
    cond_date = pd.to_datetime(data['played_at']) >= cutoff_date

    top5_df = data.loc[cond_date].groupby(agg_col_list, dropna=False).agg({
        'track_id': 'count'
        , 'track_time_played': 'sum'
    }).reset_index().rename(columns={
        'track_id': 'track_count_played'
    }).sort_values(by=sorting_dim, ascending=False).head(5)
    
    return top5_df

def create_summary_stats(data: pd.DataFrame, cutoff_date: Union[str, pd.Timestamp]) -> dict:
    """"""
    if isinstance(cutoff_date, str):
        cutoff_date = pd.to_datetime(cutoff_date)
    cond_date = pd.to_datetime(data['played_at']) >= cutoff_date
    cond_fully_played = data['track_fully_played'] == 1

    # Count stats. on songs played
    n_songs_played = data.loc[cond_date].shape[0]
    n_songs_played_fully = data.loc[cond_date & cond_fully_played].shape[0]
    completion_rate = n_songs_played_fully / n_songs_played

    # Count stats. on unique songs played
    n_unique_songs_played = data.loc[cond_date].drop_duplicates(subset=['first_artist_name', 'track_name']).shape[0]
    n_unique_songs_played_fully = data.loc[
        cond_date & cond_fully_played
    ].drop_duplicates(subset=['first_artist_name', 'track_name']).shape[0]
    
    # Stats on minutes played
    avg_track_duration = data.loc[cond_date, 'track_duration_sec'].mean()
    avg_track_time_played = data.loc[cond_date, 'track_time_played'].mean()

    # Popularity stats
    avg_track_popularity = data.loc[cond_date, 'track_popularity'].mean()
    avg_artist_popularity = data.loc[cond_date, 'artist_popularity'].mean()
    
    # Number of unique artists played
    n_unique_artists_played = data.loc[cond_date, 'first_artist_name'].nunique()   

    # Store all stats in a dictionary
    stats = {
        'n_songs_played': n_songs_played,
        'n_songs_played_fully': n_songs_played_fully,
        'completion_rate': completion_rate,
        'n_unique_songs_played': n_unique_songs_played,
        'n_unique_songs_played_fully': n_unique_songs_played_fully,
        'n_unique_artists_played': n_unique_artists_played,
        'avg_track_duration_sec': avg_track_duration,
        'avg_track_time_played_sec': avg_track_time_played,
        'avg_track_popularity': avg_track_popularity,
        'avg_artist_popularity': avg_artist_popularity
    }

    return stats
