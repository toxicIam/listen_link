import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 🔐 Настройки авторизации
SPOTIFY_CLIENT_ID = "f041013bac3d49d8a4e98c4a8a0b82e7"
SPOTIFY_CLIENT_SECRET = "4c0b9eb89ee64394a6aad4421b363c66"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SPOTIFY_PLAYLIST_ID = "2KZDetQ5mkJxtizweC1f33"

# ⚠️ Важно: у пользователя должен быть public playlist и разрешение на `playlist-modify-public`
scope = "playlist-modify-public playlist-read-private"

# 🔄 Авторизация
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))


def search_track(title: str, artist: str) -> str | None:
    query = f"{title} {artist}"
    results = sp.search(q=query, type="track", limit=1)

    tracks = results.get("tracks", {}).get("items", [])
    if tracks:
        return tracks[0]["id"]  # Spotify URI можно и как 'spotify:track:{id}'
    return None


def add_track_to_playlist(track_id: str) -> bool:
    try:
        sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [track_id])
        return True
    except Exception as e:
        print(f"Ошибка при добавлении в плейлист: {e}")
        return False


def check_track_in_playlist(track_id: str) -> bool:
    try:
        results = sp.playlist_items(SPOTIFY_PLAYLIST_ID)
        for item in results.get("items", []):
            if item.get("track", {}).get("id") == track_id:
                return True
        return False
    except Exception as e:
        print(f"Ошибка при проверке плейлиста: {e}")
        return False
