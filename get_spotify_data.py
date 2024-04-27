import requests
import urllib.parse
import numpy as np
import pandas as pd
import json

test = requests.get(url="http://localhost:5000/recently-played")
test.text