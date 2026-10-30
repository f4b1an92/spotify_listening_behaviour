from datetime import timedelta

import dash
import dash_daq as daq
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

import src.dashboard_plots.dashboard_plots_review as dbpr
from src.dashboard_helpers.dashboard_components import create_header
from src.dashboard_helpers.dashboard_data import get_data_as_of_text, get_latest_played_at, load_listening_data

data = load_listening_data()
latest_played_at = get_latest_played_at(data)

DEFAULT_OFFSET = 90
MAX_OFFSET = 365
DATE_FORMAT = '%d.%m.%Y'

TOGGLE_LABEL_STYLE = {
    'color': 'rgb(40, 210, 100)',
    'fontFamily': 'Metropolis, sans-serif',
    'fontSize': '12px',
    'fontWeight': '600',
    'whiteSpace': 'nowrap',
}
DATE_PILL_STYLE = {
    'color': 'rgb(40, 210, 100)',
    'fontFamily': 'Metropolis, sans-serif',
    'fontWeight': '600',
    'fontSize': '16px',
    'padding': '6px 16px',
    'borderRadius': '8px',
    'backgroundColor': 'rgb(55, 55, 55)',
    'whiteSpace': 'nowrap',
    'textAlign': 'center',
}
CARD_STYLE = {'backgroundColor': 'black', 'borderRadius': '20px'}


def create_filter_card() -> html.Div:
    """Build the filter card with the normalize toggle and the vertical date slider."""
    toggle = html.Div([
        html.Span('Totals', style={**TOGGLE_LABEL_STYLE, 'marginLeft': '14px'}),
        daq.BooleanSwitch(
            id='review-normalize-toggle',
            on=True,
            color='#1DB954',
            style={'margin': '0 14px', 'flexShrink': '0'},
        ),
        html.Span('Normalized', style={**TOGGLE_LABEL_STYLE, 'marginRight': '14px'}),
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'backgroundColor': 'rgb(55, 55, 55)',
        'borderRadius': '20px',
        'padding': '8px 2px',
    })
    toggle_card = html.Div(toggle, style={**CARD_STYLE, 'padding': '12px', 'flex': '0 0 auto'})

    date_filter = html.Div([
        html.Span(id='review-end-date-display', style=DATE_PILL_STYLE),
        html.Div(
            dcc.Slider(
                id='review-date-offset-input',
                vertical=True,
                min=1,
                max=MAX_OFFSET,
                step=1,
                value=DEFAULT_OFFSET,
                reverse=True,
                marks=None,
                tooltip={'placement': 'right', 'always_visible': True},
            ),
            className='review-vertical-slider',
            style={'flex': '1 1 0', 'minHeight': '0'},
        ),
        html.Span(id='review-start-date-display', style=DATE_PILL_STYLE),
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'gap': '8px',
        'flex': '1 1 0',
        'minHeight': '0',
    })
    date_card = html.Div(date_filter, style={
        **CARD_STYLE, 'padding': '12px', 'flex': '1 1 0', 'minHeight': '0', 'display': 'flex', 'flexDirection': 'column',
    })

    return html.Div([toggle_card, date_card], style={
        'width': '250px',
        'flex': '0 0 250px',
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '12px',
    })


layout = html.Div([
    create_header('Listening Behaviour - Review', active_page='Review', data_as_of_text=get_data_as_of_text(latest_played_at)),
    html.Div([
        html.Div(
            dcc.Graph(
                id='review-heatmap-graph',
                config={'responsive': True},
                style={'height': '100%', 'width': '100%'},
            ),
            style={**CARD_STYLE, 'flex': '1 1 0', 'minHeight': '260px', 'minWidth': '0', 'padding': '8px'},
        ),
        create_filter_card(),
    ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '12px', 'flex': '1 1 0', 'minHeight': '0'}),
    html.Div(
        dbpr.create_datatable(dbpr.create_datatable_input(data)),
        style={**CARD_STYLE, 'flex': '0 0 auto', 'padding': '8px', 'overflow': 'hidden'},
    ),
], style={
    'height': '100vh',
    'overflow': 'hidden',
    'backgroundColor': 'rgb(45, 45, 45)',
    'padding': '12px',
    'display': 'flex',
    'flexDirection': 'column',
    'gap': '12px',
})

# Registered after the layout exists because pages_folder='' disables Dash's layout auto-import
dash.register_page(__name__, path='/review', title='Listening Behaviour - Review', layout=layout)


@callback(
    Output('review-start-date-display', 'children'),
    Output('review-end-date-display', 'children'),
    Output('review-heatmap-graph', 'figure'),
    Output('review-datatable', 'rowData'),
    Input('review-date-offset-input', 'value'),
    Input('review-normalize-toggle', 'on'),
)
def update_review_dashboard(date_offset: int, normalized: bool) -> tuple[str, str, go.Figure, list[dict]]:
    """Update date pills, heatmap and table for the selected window."""
    end = latest_played_at
    start = end - timedelta(days=date_offset)
    date_lower, date_upper = start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

    heatmap_input = dbpr.create_heatmap_input(data, date_lower, date_upper, normalized)
    figure = dbpr.create_listening_heatmap(heatmap_input, normalized)

    played_date = data['played_at'].str[:10]
    in_range = data.loc[played_date.between(date_lower, date_upper)].copy()
    row_data = dbpr.create_datatable_input(in_range).to_dict('records')

    return start.strftime(DATE_FORMAT), end.strftime(DATE_FORMAT), figure, row_data
