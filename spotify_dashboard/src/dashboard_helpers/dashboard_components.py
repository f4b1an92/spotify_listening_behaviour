from __future__ import annotations

from dash import dcc, html

LOGO_URL = 'https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png'
NAV_PAGES = [('Summary', '/'), ('Review', '/review'), ('Compare', '/compare'), ('Discover', None)]

_BUTTON_BASE = {
    'fontFamily': 'Metropolis, sans-serif',
    'fontWeight': '600',
    'fontSize': '14px',
    'padding': '8px 18px',
    'borderRadius': '20px',
    'textDecoration': 'none',
}


def _create_nav_button(label: str, href: str | None, active: bool) -> html.Component:
    """Build one navigation button: green if active, a link if it has a route, dimmed otherwise."""
    if href is None:
        style = {**_BUTTON_BASE, 'backgroundColor': 'rgb(55, 55, 55)', 'color': 'rgb(120, 120, 120)',
                 'cursor': 'not-allowed'}
        return html.Span(label, style=style)
    if active:
        style = {**_BUTTON_BASE, 'backgroundColor': 'rgb(30, 195, 90)', 'color': 'black'}
    else:
        style = {**_BUTTON_BASE, 'backgroundColor': 'rgb(55, 55, 55)', 'color': 'rgb(40, 210, 100)'}
    return dcc.Link(label, href=href, style=style)


def create_header(title: str, active_page: str, data_as_of_text: str | None = None) -> html.Div:
    """Build the dashboard header with logo, title, optional data-as-of label and page navigation buttons."""
    buttons = [_create_nav_button(label, href, label == active_page) for label, href in NAV_PAGES]
    data_as_of_label = [] if data_as_of_text is None else [
        html.Div(data_as_of_text, style={
            'color': 'darkgrey', 'fontFamily': 'Metropolis, sans-serif', 'fontSize': '12px',
            'textAlign': 'center', 'marginTop': '4px',
        }),
    ]
    return html.Div([
        html.Img(src=LOGO_URL, style={
            'height': '50px', 'position': 'absolute', 'left': '30px', 'top': '12px',
        }),
        html.H1(title, style={
            'color': 'white', 'fontFamily': 'Metropolis, sans-serif', 'fontWeight': '600',
            'fontSize': '32px', 'margin': '0', 'textAlign': 'center',
        }),
        *data_as_of_label,
        html.Div(buttons, style={
            'position': 'absolute', 'right': '30px', 'top': '50%', 'transform': 'translateY(-50%)',
            'display': 'flex', 'gap': '10px',
        }),
    ], style={
        'position': 'relative',
        'backgroundColor': 'black',
        'borderRadius': '20px',
        'padding': '30px 12px',
        'flex': '0 0 auto',
    })
