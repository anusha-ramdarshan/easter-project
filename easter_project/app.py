import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Input(id='spotify_playlist_uri', value='spotify:playlist:5isCW7qPn5ZYmuTAzEg6Vt', type='text'),
    html.Div(id='rendered_playlist')
])

@app.callback(
    Output(component_id='rendered_playlist', component_property='children'),
    [Input(component_id='spotify_playlist_uri', component_property='value')]
)
def update_output_div(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    songs = results["items"]
    rendered = [
        html.P(children=f"{song['track']['name']}") for song in songs
    ]
    return rendered


if __name__ == '__main__':
    app.run_server(debug=True)

