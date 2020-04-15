import json
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import spotipy
from dash.dependencies import MATCH, Input, Output, State
from flask_caching import Cache
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
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".cache"})

app.layout = html.Div(
    [
        dcc.Input(
            id="spotify_playlist_uri",
            value="spotify:playlist:5isCW7qPn5ZYmuTAzEg6Vt",
            type="text",
        ),
        html.Button("Play/Pause", id="playing", n_clicks=0),
        html.Div(id="rendered_playlist", className="playlist_container",),
        html.Div(id="ignored", style={"display": "none"}),
    ]
)


@app.callback(
    Output(component_id="playing", component_property="children"),
    [Input(component_id="playing", component_property="n_clicks")],
)
def play_pause(n_clicks):
    if n_clicks == 0:
        pass
    elif n_clicks % 2 == 0:
        # TODO: ask whether the player is playing, and make it do the opposite
        sp.start_playback(device_id="ebd0aeab1bdf270978926d619a400d8a4af9976b")
        return "Pause"
    else:
        sp.pause_playback(device_id="ebd0aeab1bdf270978926d619a400d8a4af9976b")
        return "Play"

    return "Play/Pause"


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
    print(json.dumps(sp.current_playback(), indent=4))
    print(json.dumps(sp.devices(), indent=4))
    return rendered


@cache.memoize()
def get_audio_analysis(uri):
    return sp.audio_analysis(uri)


def render_song(song):
    uri = song["track"]["uri"]
    analysis = get_audio_analysis(uri)
    beat_durations = []
    for beat in analysis["beats"]:
        beat_durations.append(beat["duration"])
    mean_beat_duration = np.mean(beat_durations)

    bpm = int(60 / mean_beat_duration)
    return html.Div(
        children=[
            html.Button(
                "Play", id={"type": "play_song_button", "index": uri}, n_clicks=0,
            ),
            html.Div(id={"type": "play_song_output", "index": uri}),
            html.Div(children=f"{song['track']['name']}"),
            html.Div(children=f"bpm = {bpm}"),
        ]
    )


@app.callback(
    Output(
        component_id={"type": "play_song_output", "index": MATCH},
        component_property="children",
    ),
    [
        Input(component_id="spotify_playlist_uri", component_property="value"),
        Input(
            component_id={"type": "play_song_button", "index": MATCH},
            component_property="n_clicks",
        ),
    ],
    [
        State(
            component_id={"type": "play_song_button", "index": MATCH},
            component_property="id",
        )
    ],
)
def handle_play_song_button(playlist, n_clicks, id):
    if n_clicks == 0:
        return ""
    sp.start_playback(
        device_id=None,
        context_uri=playlist,
        uris=None,
        offset={"uri": id["index"]},
        position_ms=None,
    )

    print(playlist, n_clicks, id)
    return f"{n_clicks}"


def embed_link(song):
    return f"https://open.spotify.com/embed/track/{song['track']['id']}"


if __name__ == "__main__":
    app.run_server(debug=True)
