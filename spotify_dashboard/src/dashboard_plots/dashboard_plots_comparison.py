import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go


def song_comparison_polar_chart(data: pd.DataFrame, feature_name: str, idx_main: int, idx_ref: int) -> go.Figure:
    """
    This function generates a polar bar chart visualization that compares either 'loudness'
    or 'tempo' values between a main track and a reference track. The values are displayed
    as circular bars with different radii, where the main track appears on the outer circle
    and the reference track on the inner circle.

    Args:
        data (pd.DataFrame): DataFrame containing song data with columns including 
            'track_name', 'loudness', and 'tempo'.
        feature_name (str): Name of the feature to compare. Must be either 'loudness' 
            or 'tempo'.
        idx_main (int): Index of the main track in the DataFrame.
        idx_ref (int): Index of the reference track in the DataFrame.
    Returns:
        go.Figure: A Plotly figure object containing the polar comparison chart with:
            - Outer circle (green) representing the main track's feature value
            - Inner circle (blue) representing the reference track's feature value
            - Background circles for visual context
            - Center annotation displaying both values with units
            - Feature-specific title and formatting
    Notes:
        - Loudness values are displayed in decibels (dB) with 1 decimal place
        - Tempo values are displayed in beats per minute (bpm) with no decimals
        - Values are normalized to degrees (0-360) for polar representation
        - The chart uses a dark theme with colored bars matching Spotify's aesthetic
    """
    # Get track names
    track_main = data.loc[idx_main, 'track_name']
    track_ref = data.loc[idx_ref, 'track_name']

    # Get feature values
    if feature_name == 'loudness':
        feature_value_main = data.loc[idx_main, 'loudness']
        feature_value_ref = data.loc[idx_ref, 'loudness']
        feature_unit = 'dB'
        feature_title = 'Loudness in Decibels'
        feature_rounding_decimal = 1
    else:
        feature_value_main = data.loc[idx_main, 'tempo']
        feature_value_ref = data.loc[idx_ref, 'tempo']
        feature_unit = 'bpm'
        feature_title = 'Tempo in Beats per Minute'
        feature_rounding_decimal = 0

    # Normalize values to degrees (0-360)
    if feature_name == 'loudness':
        normalization_factor_cirle = 360 / (data[feature_name].min() - data[feature_name].max())  # loudness ranges from -60 dB to 0 dB
        feature_main_deg = 360 - (normalization_factor_cirle * feature_value_main)
        feature_ref_deg = 360 - (normalization_factor_cirle * feature_value_ref)
    else:
        normalization_factor_cirle = 360 / data[feature_name].max()
        feature_main_deg = normalization_factor_cirle * feature_value_main
        feature_ref_deg = normalization_factor_cirle * feature_value_ref

    # Create figure
    fig = go.Figure()

    # Add outer circle (border)
    fig.add_trace(go.Scatterpolar(
        r=[max(base + 2 for base in [12, 10]) + 2] * 360,
        theta=list(range(360)),
        mode='lines',
        line=dict(color='white', width=4),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Background circles (inside border circle)
    for circle_pos, base_dist in zip(['outer', 'inner'], [12, 8]):
        fig.add_trace(go.Barpolar(
            r=[2],
            theta=[180], # theta = center of the bar, thus if bar should start at 0, theta should be equal to half the length of the bar (i.e. loudness_main_deg / 2)  
            width=[360],
            marker=dict(color='rgba(80, 80, 80, 0.5)', line=dict(color='rgba(80, 80, 80, 0.5)', width=4)),
            name=f'{track_main} - {feature_name.capitalize()} - Background ({circle_pos})',
            hoverinfo='skip',
            base=base_dist
        ))

    # Main Track (outer circle)
    fig.add_trace(go.Barpolar(
        r=[2],
        theta=[feature_main_deg / 2], # theta = center of the bar, thus if bar should start at 0, theta should be equal to half the length of the bar (i.e. loudness_main_deg / 2)  
        width=[feature_main_deg],
        #marker=dict(color='rgb(57, 255, 0)', line=dict(color='rgb(57, 255, 0)', width=4)), # neon green
        #marker=dict(color='rgb(30, 215, 96)', line=dict(color='rgb(30, 215, 96)', width=4)), # darker green
        marker=dict(color='rgb(30, 195, 90)', line=dict(color='rgb(30, 195, 90)', width=4)), # green that matches spotify logo - slightly darker b/c the color code we use for text appears too bright inside the charts
        name=f'{track_main} - {feature_name.capitalize()}',
        #hovertemplate=f'<b>{track_main}</b><br>Loudness: {loudness_main:.1f} dB<extra></extra>',
        hoverinfo='skip',
        base=12
    ))

    # Reference track (inner circle)
    fig.add_trace(go.Barpolar(
        r=[2],
        theta=[feature_ref_deg / 2], # theta = center of the bar, thus if bar should start at 0, theta should be equal to half the length of the bar (i.e. loudness_ref_deg / 2)  
        width=[feature_ref_deg],
        marker=dict(color='rgb(0, 191, 255)', line=dict(color='rgb(0, 191, 255)', width=4)),
        name=f'{track_ref} - {feature_name.capitalize()}',
        #hovertemplate=f'<b>{track_ref}</b><br>Loudness: {loudness_ref:.1f} dB<extra></extra>',
        hoverinfo='skip',
        base=8
    ))

    # Add text annotations in the center
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref='paper',
        yref='paper',
        #text=f'<b style="color:rgb(57, 255, 0)">{loudness_main:.1f} dB</b><br><b style="color:rgb(0, 191, 255)">{loudness_ref:.1f} dB</b>',
        #text=f'<b style="color:rgb(30, 215, 96)">{feature_value_main:.{feature_rounding_decimal}f} {feature_unit}</b><br><b style="color:rgb(0, 191, 255)">{feature_value_ref:.{feature_rounding_decimal}f} {feature_unit}</b>',
        text=f'<b style="color:rgb(30, 195, 90)">{feature_value_main:.{feature_rounding_decimal}f} {feature_unit}</b><br><b style="color:rgb(0, 191, 255)">{feature_value_ref:.{feature_rounding_decimal}f} {feature_unit}</b>', # green that mathes the spotify logo - slightly darker b/c the color code we use for text appears too bright inside the charts
        showarrow=False,
        font=dict(size=18, color='white', family='Metropolis, sans-serif'),
        align='center'
    )

    # Update layout
    fig.update_layout(
        paper_bgcolor='black',
        polar=dict(
            bgcolor='black',
            radialaxis=dict(visible=False),
            angularaxis=dict(
                visible=False,
                rotation=90,
                direction="clockwise",
            )
        ),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),  # Reduce left, right, top, bottom margins
        #title=dict(
        #    text=feature_title,
        #    font=dict(size=20, color='darkgrey', family='Metropolis, sans-serif', weight='bold'),
        #    x=0.5,
        #    xanchor='center',
        #    y=0.9,
        #    yanchor='top'
        #)
    )
    return fig


def song_comparison_audio_feature_bar_chart(data: pd.DataFrame, track_idx: int, track_type: str) -> go.Figure:
    """
    Create a horizontal bar chart displaying audio features for a single track.
    This function generates a Plotly bar chart that visualizes selected audio features
    (acousticness, danceability, energy, instrumentalness, and valence) for a specified
    track. The visualization can be customized for either a 'main' track or a comparison
    track (specified via track_type='ref') with different colors and label positioning.

    Args:
        data (pd.DataFrame): DataFrame containing track information and audio features.
            Must include columns: 'track_name', 'acousticness', 'danceability', 
            'energy', 'instrumentalness', and 'valence'.
        track_idx (int): Index of the track in the DataFrame to visualize.
        track_type (str): Type of track visualization. Use 'main' for the primary track
            (displayed in green with right-aligned labels) or any other value for 
            comparison tracks (displayed in blue with left-aligned labels).
    Returns:
        go.Figure: A Plotly Figure object containing the horizontal bar chart with
            black background, white text, and customized styling based on track type.
    Notes:
        - Audio feature values are displayed with 2 decimal precision
        - The chart uses a dark theme with black background and white text
        - Grid lines are semi-transparent white
        - Legend is hidden to maintain clean visualization
    """

    # Get the audio features
    features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'valence']
    features_labels = ['Acoustic', 'Danceability', 'Energy', 'Instrumental', 'Valence']
    track_name = data.loc[track_idx, 'track_name'] # Get track names
    track_values = data.loc[track_idx, features].values.tolist()
    
    # Customize based on track type
    if track_type == 'main':
        features_labels = [f"{fl}  " for fl in features_labels] 
        #marker_color = 'rgb(57, 255, 0)'  # Neon green
        #marker_color = 'rgb(30, 215, 96)'  # darker green
        marker_color = 'rgb(30, 195, 90)'  # green that matches spotify logo - slightly darker b/c the color code we use for text appears too bright inside the charts
        x_tick_range = [0, 1.08]
        y_axis_side = 'left'
    else:
        features_labels = [f"  {fl}" for fl in features_labels] 
        marker_color = 'rgb(0, 191, 255)'  # Neon blue
        x_tick_range = [1.08, 0]
        y_axis_side = 'right'

    # Create figure
    fig = go.Figure()

    # Add bars for main track
    fig.add_trace(go.Bar(
        y=features_labels,
        x=track_values,
        orientation='h',
        name=track_name,
        marker=dict(color=marker_color),
        text=[f'  {v:.2f}' for v in track_values],
        textposition='outside',
        hovertemplate='<b>Main Track:</b> %{fullData.name}<br><b>%{y}:</b> %{x:.2f}<extra></extra>',
        width=0.4
    ))

    # Update layout
    fig.update_layout(
        barmode='group',
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='darkgrey', size=14, family='Metropolis, sans-serif', weight='bold'),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.2)',
            range=x_tick_range
        ),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)',side=y_axis_side),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10)  # Reduce left, right, top, bottom margins
    )

    return fig


def song_comparison_radar_chart(data: pd.DataFrame, idx_main: int, idx_ref: int) -> go.Figure:
    """
    This function generates a radar chart that visualizes and compares five audio features
    (acousticness, danceability, energy, instrumentalness, and valence) between a main track
    and a reference track.
    Args:
        data (pd.DataFrame): DataFrame containing song data with audio features and track names.
                            Must include columns: 'acousticness', 'danceability', 'energy',
                            'instrumentalness', 'valence', and 'track_name'.
        idx_main (int): Index of the main track in the DataFrame to be compared.
        idx_ref (int): Index of the reference track in the DataFrame to compare against.
    Returns:
        go.Figure: A Plotly Figure object containing the radar chart with two overlapping pentagons:
                  - Reference track: displayed in blue (Dodger Blue)
                  - Main track: displayed in green (Spotify green)
                  The chart uses a black background with white gridlines and features hoverable
                  data points showing exact feature values.
    Note:
        - All audio features are expected to be normalized between 0 and 1.
        - The chart uses a linear grid shape with a black background matching Spotify's theme.
        - Legend is hidden; tracks are distinguished by color (blue for reference, green for main).
    """
    # Get audio features
    features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'valence']
    features_labels = ['Acoustic', '  Danceability', '  Energy', 'Instrumental  ', 'Valence  ']
    values_main = data.loc[idx_main, features].values.tolist()
    values_ref = data.loc[idx_ref, features].values.tolist()

    # Create radar plot
    fig = go.Figure()

    # Pentagon for referenece track
    fig.add_trace(go.Scatterpolar(
        r=values_ref,
        theta=features_labels,
        fill='toself',
        name=data.loc[idx_ref, 'track_name'],
        fillcolor='rgba(135, 206, 250, 0.4)',
        line=dict(color='rgba(30, 144, 255, 0.9)'), # Dodger Blue
        marker=dict(
            size=10,
            color='rgb(30, 144, 255)', # Dodger Blue
            symbol='circle'
        ),
        hovertemplate='<b>Reference Track:</b> %{fullData.name}<br><b>%{theta}:</b> %{r:.3f}<extra></extra>'
    ))

    # Pentagon for main track
    fig.add_trace(go.Scatterpolar(
        r=values_main,
        theta=features_labels,
        fill='toself',
        name=data.loc[idx_main, 'track_name'],
        fillcolor='rgba(30, 215, 96, 0.4)',
        #line=dict(color='rgba(57, 255, 0, 0.9)'), # neon green
        line=dict(color='rgba(30, 215, 96, 0.9)'), # darker green
        marker=dict(
            size=10,
            #color='rgb(57, 255, 0)',  # neon green
            color='rgb(30, 215, 96)',  # darker green
            symbol='circle'
        ),
        hovertemplate='<b>Main Track:</b> %{fullData.name}<br><b>%{theta}:</b> %{r:.3f}<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor='black',
        showlegend=False,
        margin=dict(l=20, r=20, t=5, b=40),  # Reduce left, right, top, bottom margins
        polar=dict(
            bgcolor='black',
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridwidth=2,
                gridcolor='white',
                linewidth=2,
                linecolor='white',
                color='rgba(255, 255, 255, 0.7)',
                showticklabels=False,
            ),
            angularaxis=dict(
                gridcolor='white',
                gridwidth=2,
                linewidth=2,
                linecolor='white',
                #tickfont=dict(size=17, color='rgba(30, 215, 96, 0.9)'),
                tickfont=dict(size=18, color='darkgrey', family='Metropolis, sans-serif', weight='bold'),
                showticklabels=True,
                rotation=270,
            ),
            #gridshape='circular'
            gridshape='linear'
        )
    )
    return fig

