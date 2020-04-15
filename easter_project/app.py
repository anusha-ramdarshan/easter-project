import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-read-playback-state,user-modify-playback-state"
token = spotipy.util.prompt_for_user_token(
    "eosimias",
    scope=scope,
    client_id=None,
    client_secret=None,
    redirect_uri=None,
    cache_path=None,
    oauth_manager=None,
    show_dialog=False,
)
sp = spotipy.Spotify(auth=token)
print("logged into spotify")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dcc.Input(
            id="spotify_playlist_uri",
            value="spotify:playlist:5isCW7qPn5ZYmuTAzEg6Vt",
            type="text",
        ),
        dcc.Checklist(
            id="checklist", options=[{"label": "Playing", "value": "playing"}]
        ),
        html.Div(id="rendered_playlist", className="playlist_container",),
        html.Div(id="ignored", style={"display": "none"}),
    ]
)


@app.callback(
    Output(component_id="ignored", component_property="children"),
    [Input(component_id="checklist", component_property="value")],
)
def play_pause(checked):
    if checked == ["playing"]:
        sp.start_playback()
    else:
        sp.pause_playback()
    return []


@app.callback(
    Output(component_id="rendered_playlist", component_property="children"),
    [Input(component_id="spotify_playlist_uri", component_property="value")],
)
def update_output_div(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    songs = results["items"]
    rendered = [render_song(song) for song in songs]
    spotipy.util.prompt_for_user_token(
        "eosimias",
        scope=None,
        client_id=None,
        client_secret=None,
        redirect_uri=None,
        cache_path=None,
        oauth_manager=None,
        show_dialog=False,
    )
    sp.current_playback()
    return rendered


def render_song(song):
    return html.Div(children=[html.Div(children=f"{song['track']['name']}"),])


def embed_link(song):
    return f"https://open.spotify.com/embed/track/{song['track']['id']}"


if __name__ == "__main__":
    app.run_server(debug=True)

