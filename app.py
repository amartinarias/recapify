from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from creds import *
from main import get_recently_played_song


app = Flask(__name__)

# signs the session cookie
app.secret_key = "d5cf15a0d4b04e5699ec1d0e769e6177"
app.config['SESSION_COOKIE_NAME'] = "Lydia's Cookie"  # session allows you to log in during the same session
TOKEN_INFO = "token_info"


@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    # saving token info in the session
    session[TOKEN_INFO] = token_info
    return redirect("getTracks")


@app.route('/getTracks')
def get_tracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    iter = 0
    while True:
        items = sp.current_user_saved_tracks(limit=50, offset=iter * 50)['items']
        iter += 1
        all_songs += items
        if len(items) < 50:
            break
    return str(len(all_songs))


@app.route('/getArtists')
def get_artist():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_artists(limit=20, offset=0, time_range='medium_term')
    for items in results['items']:
        return str(items['name'])


@app.route('/getRecentlyPlayed')
def get_recently_played():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    last_song_played = get_recently_played_song
    return render_template("recently_played.html", get_recently_played=last_song_played)


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=url_for('redirect_page', _external=True),
        scope="user-library-read")


app.run(debug=True)
if __name__ == "__main__":
    app.run(debug=True)

