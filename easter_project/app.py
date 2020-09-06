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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
sp = spotipy.Spotify(auth=token, requests_timeout=10)
print("logged into spotify")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".cache"})


def get_layout():
    return html.Div(
        [
            dcc.Input(
                id="spotify_playlist_uri",
                value="spotify:playlist:5isCW7qPn5ZYmuTAzEg6Vt",
                type="text",
            ),
            html.Button("Play/Pause", id="playing", n_clicks=0),
            html.Div(
                id="summary_plot",
                children=[render_summary("spotify:playlist:5isCW7qPn5ZYmuTAzEg6Vt")],
            ),
            html.Div(
                children=[
                    html.Div(
                        [
                            dcc.Markdown(
                                """For more information on a song, click on a point in the graph"""
                            ),
                            html.Pre(id="click-data"),
                        ]
                    )
                ],
            ),
            html.Div(id="rendered_playlist", className="playlist_container",),
            html.Div(id="ignored", style={"display": "none"}),
        ]
    )


app.layout = get_layout


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
    Output(component_id="summary_plot", component_property="children"),
    [Input(component_id="spotify_playlist_uri", component_property="value")],
)
def update_summary_output_div(playlist_id):
    results = get_audio_features_for_playlist(playlist_id)
    # print(json.dumps(results, indent=4))
    rendered = render_summary(playlist_id)
    return rendered


@cache.memoize()
def get_audio_features_for_playlist(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    songs = results["items"]
    tracks = [song["track"]["id"] for song in songs]
    names = [song["track"]["name"] for song in songs]
    return sp.audio_features(tracks=tracks), names


def plot_playlist_data(playlist_id):
    features, names = get_audio_features_for_playlist(playlist_id)

    playlist_info = sp.playlist(playlist_id)
    # print(json.dumps(playlist_info, indent=4), "<--look at dis one")

    x = list(range(1, len(features)))
    y0 = [feature["energy"] for feature in features]
    y1 = [feature["danceability"] for feature in features]
    y2 = [feature["valence"] for feature in features]
    y3 = [feature["tempo"] for feature in features]

    # Create traces
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=x, y=y0, mode="lines+markers", name="energy"), secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=x, y=y1, mode="lines+markers", name="danceability"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=x, y=y2, mode="lines+markers", name="valence"), secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=x, y=y3, name="tempo/bpm"), secondary_y=True,
    )

    # Add figure title

    fig.update_layout(
        title_text=f"{playlist_info['name']} by {playlist_info['owner']['display_name']}"
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="energy/danceability/valence", secondary_y=False)
    fig.update_yaxes(title_text="Tempo in beats per minute", secondary_y=True)

    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))

    fig.update_layout(xaxis=dict(tickmode="linear", tick0=1, dtick=1))
    fig.update_layout(xaxis=dict(tickmode="array", tickvals=x, ticktext=names))
    fig.update_layout(template="simple_white", clickmode="event+select")

    return dcc.Graph(id="playlist_summary_plot", figure=fig)


def render_summary(playlist_id):

    graph = plot_playlist_data(playlist_id)
    return html.Div(children=[graph,], className="song_container",)


@app.callback(
    Output("click-data", "children"),
    [
        Input(component_id="spotify_playlist_uri", component_property="value"),
        Input("playlist_summary_plot", "clickData"),
    ],
)
def display_click_data(playlist, clickData):

    return plot_detailed_song(playlist, clickData)


def plot_detailed_song(playlist, clickData):
    if clickData is None:
        return "waiting for click"

    tracks = sp.playlist_tracks(playlist)["items"]
    song_number = clickData["points"][0]["x"]
    song = tracks[song_number]

    analysis = get_audio_analysis(song["track"]["uri"])
    last = analysis["sections"][-1]
    x = np.array(
        [section["start"] for section in analysis["sections"]]
        + [last["start"] + last["duration"]]
    )  # time
    y = np.array(
        [section["loudness"] for section in analysis["sections"]] + [last["loudness"]]
    )  # loudness

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name="Loudness", line_shape="hv"))

    fig.update_traces(hoverinfo="text+name", mode="lines+markers")
    fig.update_layout(legend=dict(y=0.5, traceorder="reversed", font_size=16))

    return dcc.Graph(figure=fig)


@app.callback(
    Output(component_id="rendered_playlist", component_property="children"),
    [Input(component_id="spotify_playlist_uri", component_property="value")],
)
def update_output_div(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    songs = results["items"]
    rendered = [render_song(song) for song in songs]
    return rendered


@cache.memoize()
def get_audio_analysis(uri):
    return sp.audio_analysis(uri)


def plot_song_data(uri):
    analysis = get_audio_analysis(uri)
    last = analysis["sections"][-1]
    x = np.array(
        [section["start"] for section in analysis["sections"]]
        + [last["start"] + last["duration"]]
    )  # time
    y = np.array(
        [section["loudness"] for section in analysis["sections"]] + [last["loudness"]]
    )  # loudness

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name="Loudness", line_shape="hv"))

    fig.update_traces(hoverinfo="text+name", mode="lines+markers")
    fig.update_layout(legend=dict(y=0.5, traceorder="reversed", font_size=16))

    return dcc.Graph(figure=fig)


@cache.memoize()
def get_bpm(uri):
    analysis = get_audio_analysis(uri)
    beat_durations = []
    for beat in analysis["beats"]:
        beat_durations.append(beat["duration"])
    mean_beat_duration = np.mean(beat_durations)
    return int(60 / mean_beat_duration)


def render_song(song):
    uri = song["track"]["uri"]
    bpm = get_bpm(uri)

    # graph = plot_song_data(uri)
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children=f"{song['track']['artists'][0]['name']}"),
                    html.Div(children=f"{song['track']['name']}"),
                    html.Button(
                        "Play",
                        id={"type": "play_song_button", "index": uri},
                        n_clicks=0,
                    ),
                ],
                className="song_header",
            ),
            html.Div(id={"type": "play_song_output", "index": uri}),
            html.Div(children=f"bpm = {bpm}"),
            # graph,
        ],
        className="song_container",
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
