import sys
import os
import yaml
import webbrowser
from spotipy.oauth2 import SpotifyOAuth

# Define main path (this should give the same path independant of the execution env (i.e. terminal, Jupyter NB or IDE))
if sys.stdin.isatty() & sys.stdout.isatty():
    MAIN_PATH = os.path.dirname(os.path.abspath(__file__))  # for terminal
elif 'ipykernel' in sys.modules:
    MAIN_PATH = os.path.dirname(os.path.abspath(""))  # for Jupyter notebook
else:
    MAIN_PATH = os.getcwd()  # for IDE

DATA_PATH = MAIN_PATH + '\\data'

sys.path.extend([
    MAIN_PATH
])

# Load config & use it to define constants
with open(MAIN_PATH + '\\resources\\config.yaml', 'r') as f:
    config = yaml.safe_load(f)

def init_user_auth():
    """Initiates user authentification process with Spotify API."""
    sp_oauth = SpotifyOAuth(
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        redirect_uri=config['redirect_uri_aws'],
        scope='user-read-private user-read-email user-read-recently-played',
        open_browser=False
    )
    auth_url = sp_oauth.get_authorize_url()
    webbrowser.open(auth_url)

    return "Auth linked was opened succssfully. Please check your browser if authentification was successful as well."


if __name__ == "__main__":
    init_user_auth()
