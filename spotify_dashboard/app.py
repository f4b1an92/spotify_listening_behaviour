import os
import sys

import dash
import dash_ag_grid as dag
from dash import Dash

PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(PATH)  # makes `src` importable

# pages_folder is empty on purpose: pages are registered by the explicit imports below
app = Dash(
    __name__,
    use_pages=True,
    pages_folder=PATH+'/src/pages',
    assets_folder=os.path.join(PATH, 'assets'),
    external_stylesheets=[dag.themes.BASE, dag.themes.ALPINE],
)

import src.pages.spotify_dashboard_summary  # noqa: E402,F401  (registers the page)
import src.pages.spotify_dashboard_review  # noqa: E402,F401
import src.pages.spotify_dashboard_comparison  # noqa: E402,F401

app.layout = dash.page_container

if __name__ == '__main__':
    app.run(debug=os.environ.get('DASH_DEBUG', '1') == '1', port=8055)
