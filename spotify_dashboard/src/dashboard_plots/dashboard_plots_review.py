from __future__ import annotations

import dash_ag_grid as dag
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


GREEN = 'rgb(30, 195, 90)'
GREY = 'rgb(130, 130, 130)'
WEEKDAYS = ['Mon  ', 'Tue ', 'Wed  ', 'Thu  ', 'Fri  ', 'Sat  ', 'Sun  ']
HOURS = [f'{hour:02d}' for hour in range(24)]


def _create_review_dashboard_input(data: pd.DataFrame) -> pd.DataFrame:
    """"""
    data = data.copy()

    # Split played_at into date and time
    data['played_at_date'] = pd.to_datetime(data['played_at']).dt.strftime('%Y-%m-%d')
    data['played_at_time'] = pd.to_datetime(data['played_at']).dt.strftime('%H:%M:%S')
    data['played_at_weekday'] = pd.to_datetime(data['played_at_date']).dt.weekday
    data['played_at_hour'] = pd.to_datetime(data['played_at_time'], format='%H:%M:%S').dt.strftime('%H')

    # Ensure capitalization in simplified_main_genre
    data['simplified_main_genre'] = [str(i).capitalize() for i in data['simplified_main_genre']]

    # Convert track_fully_played from dummy to Yes/No
    data['track_fully_played'] = data['track_fully_played'].apply(lambda x: 'Yes' if x == 1 else 'No') 

    # Sort by played_at to get data into chronological order
    data_sorted = data.sort_values(by='played_at', ascending=False).reset_index(drop=True)

    data_sorted = data_sorted.rename(columns={'energy': 'track_energy'})
    
    return data_sorted

def create_datatable_input(data: pd.DataFrame) -> pd.DataFrame:
    """"""
    # Prepare the data using the review dashboard input function to ensure all necessary columns and formatting are present
    data = _create_review_dashboard_input(data)

    # Select Required Columns for data table 
    required_col_list = ['track_name', 'album_image_url', 'track_energy', 'combined_artist_names', 'simplified_main_genre', 'track_duration_min_sec', 'played_at_date', 'played_at_time', 'track_fully_played']
    data_reduced = data.loc[:, required_col_list]

    # Fill missing values for track_energy with 0
    data_reduced['track_energy'] = data_reduced['track_energy'].fillna(0)

    # Rename columns into user-friendly names that can be displayed in the dashboard
    data_reduced.columns = ['Track', 'Album', 'Energy', 'Artist', 'Genre', 'Duration', 'Played on', 'Played at', 'Fully Played']

    return data_reduced

def create_datatable(data: pd.DataFrame) -> dag.AgGrid:
    """Build the listening history AG Grid from the output of create_datatable_input()."""
    text_filter = {'filter': 'agTextColumnFilter', 'floatingFilter': True}
    column_defs = [
        {'field': 'Album', 'headerName': 'Album', 'pinned': 'left', 'width': 110,
         'sortable': False, 'filter': False, 'resizable': False, 'cellRenderer': 'AlbumCover'},
        {'field': 'Track', 'flex': 3, 'minWidth': 220, **text_filter},
        {'field': 'Artist', 'flex': 2, 'minWidth': 160, **text_filter},
        {'field': 'Genre', 'flex': 2, 'minWidth': 140, **text_filter},
        {'field': 'Energy', 'flex': 2, 'minWidth': 150, 'cellRenderer': 'EnergyBar'},
        {'field': 'Duration', 'flex': 1, 'minWidth': 100},
        {
            'field': 'Played on', 'flex': 1, 'minWidth': 130,
            'filter': 'agDateColumnFilter', 'floatingFilter': True,
            'filterParams': {
                'comparator': {'function': 'dateComparator'},
                'filterOptions': ['equals', 'lessThan', 'greaterThan', 'inRange'],
                'inRangeInclusive': True,
                'maxNumConditions': 1,
                'buttons': ['reset'],
            },
        },
        {'field': 'Played at', 'flex': 1, 'minWidth': 130},
        {
            'field': 'Fully Played', 'flex': 1, 'minWidth': 130,
            'headerClass': 'ag-center-header',
            'cellStyle': {
                'styleConditions': [
                    {'condition': "params.value == 'Yes'", 'style': {'color': GREEN, 'justifyContent': 'center'}},
                ],
                'defaultStyle': {'color': GREY, 'justifyContent': 'center'},
            },
        },
    ]
    return dag.AgGrid(
        id='review-datatable',
        rowData=data.to_dict('records'),
        columnDefs=column_defs,
        defaultColDef={'sortable': True, 'filter': False, 'resizable': True},
        dashGridOptions={
            'theme': 'legacy',
            'pagination': True,
            'paginationPageSize': 5,
            'paginationPageSizeSelector': False,
            'rowHeight': 44,
            'headerHeight': 38,
            'floatingFiltersHeight': 38,
            'domLayout': 'autoHeight',
        },
        className='ag-theme-alpine-dark review-datatable',
        style={'width': '100%', 'height': None},
    )

def create_heatmap_input(
    data: pd.DataFrame,
    date_lower: str,
    date_upper: str,
    normalized: bool = True
) -> pd.DataFrame:
    """Prepare a complete weekday-by-hour listening matrix in minutes."""
    # Prepare the data using the review dashboard input function to ensure all necessary columns and formatting are present
    data = _create_review_dashboard_input(data)

    played_dates = pd.to_datetime(data['played_at_date'], errors='coerce')
    lower_bound = pd.to_datetime(date_lower)
    upper_bound = pd.to_datetime(date_upper)
    weekdays = pd.to_numeric(data['played_at_weekday'], errors='coerce')
    hours = pd.to_numeric(data['played_at_hour'], errors='coerce')
    played_seconds = pd.to_numeric(data['track_time_played'], errors='coerce')

    selected = pd.DataFrame({
        'weekday': weekdays,
        'hour': hours,
        'minutes': played_seconds / 60,
    }, index=data.index).loc[
        played_dates.between(lower_bound, upper_bound, inclusive='both')
    ].dropna(subset=['weekday', 'hour', 'minutes'])
    selected = selected.loc[
        selected['weekday'].between(0, 6) & selected['hour'].between(0, 23)
    ]
    selected['weekday'] = selected['weekday'].astype(int)
    selected['hour'] = selected['hour'].astype(int)

    grouped = selected.groupby(['weekday', 'hour'])['minutes'].sum()
    heatmap_df = grouped.unstack('hour').reindex(
        index=range(7), columns=range(24), fill_value=0
    ).fillna(0)
    heatmap_df.index = WEEKDAYS
    heatmap_df.columns = HOURS

    if normalized:
        number_of_weeks = max(round((pd.to_datetime(date_upper) - pd.to_datetime(date_lower)).days / 7), 1)
        heatmap_df = heatmap_df / number_of_weeks

    heatmap_df.attrs['hourly_totals'] = heatmap_df.sum(axis=0).rename('minutes')
    heatmap_df.attrs['weekday_totals'] = heatmap_df.sum(axis=1).rename('minutes')
    return heatmap_df


def create_listening_heatmap(heatmap_df: pd.DataFrame, normalized: bool = True) -> go.Figure:
    """Build a listening heatmap with aligned hourly and weekday totals."""
    matrix = heatmap_df.reindex(index=WEEKDAYS, columns=HOURS, fill_value=0)
    hourly_totals = heatmap_df.attrs.get('hourly_totals', matrix.sum(axis=0))
    weekday_totals = heatmap_df.attrs.get('weekday_totals', matrix.sum(axis=1))
    hourly_totals = hourly_totals.reindex(HOURS, fill_value=0)
    weekday_totals = weekday_totals.reindex(WEEKDAYS, fill_value=0)
    durations = [
        [f'{float(value):.1f} min' for value in row]
        for row in matrix.to_numpy()
    ]
    heatmap_max = max(float(matrix.to_numpy().max()), 1)

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{'type': 'xy'}, {'type': 'xy'}], [{'type': 'heatmap'}, {'type': 'xy'}]],
        shared_xaxes='columns',
        shared_yaxes='rows',
        row_heights=[0.25, 0.75],
        column_widths=[0.82, 0.18],
        horizontal_spacing=0.04,
        vertical_spacing=0.04,
    )

    fig.add_trace(
        go.Bar(
            x=HOURS,
            y=hourly_totals,
            marker_color='rgb(30, 195, 90)',
            text=[f'{value:.0f}' for value in hourly_totals],
            textposition='outside',
            cliponaxis=False,
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(
            x=HOURS,
            y=WEEKDAYS,
            z=matrix.to_numpy(),
            customdata=durations,
            colorscale=[
                [0, 'rgb(0, 0, 0)'],
                [0.35, 'rgb(0, 70, 30)'],
                [0.7, 'rgb(8, 130, 55)'],
                [1, 'rgb(30, 195, 90)'],
            ],
            zmin=0,
            zmax=heatmap_max,
            hovertemplate='<b>%{y}</b><br>%{x}:00 - %{customdata}<extra></extra>',
            showscale=False,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=weekday_totals,
            y=WEEKDAYS,
            orientation='h',
            marker_color='rgb(30, 195, 90)',
            text=[f'{value:.0f}' for value in weekday_totals],
            textposition='outside',
            cliponaxis=False,
            showlegend=False,
            hoverinfo='skip',
        ),
        row=2,
        col=2,
    )

    if normalized:
        title_suffix = '(normalized)'
    else:
        title_suffix = '(totals)'

    grid_color = 'rgba(255, 255, 255, 0.2)'
    fig.update_layout(
        autosize=True,
        title=f'Listening Time by Weekday and Hour of the Day {title_suffix}',
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', size=14, family='Metropolis, sans-serif'),
        margin=dict(t=55, l=55, r=75, b=55),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor=grid_color, showgrid=True, zeroline=False)
    fig.update_xaxes(
        categoryorder='array', categoryarray=HOURS, row=1, col=1
    )
    fig.update_xaxes(
        categoryorder='array', categoryarray=HOURS, row=2, col=1
    )
    fig.update_yaxes(gridcolor=grid_color, showgrid=True, zeroline=False)
    fig.update_yaxes(
        categoryorder='array',
        categoryarray=WEEKDAYS,
        autorange='reversed',
        row=2,
    )
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, row=2, col=2)
    fig.update_xaxes(showgrid=False, row=1, col=1)
    fig.update_yaxes(showgrid=False, row=1, col=1)
    fig.update_xaxes(showgrid=False, showticklabels=False, row=2, col=2)
    fig.update_yaxes(showgrid=False, row=2, col=2)
    fig.update_xaxes(title_text='Hour', row=2, col=1)

    max_hourly = max(float(hourly_totals.max()), 1)
    max_weekday = max(float(weekday_totals.max()), 1)
    fig.update_yaxes(range=[0, max_hourly * 1.2], row=1, col=1)
    fig.update_xaxes(range=[0, max_weekday * 1.2], row=2, col=2)
    return fig