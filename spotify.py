import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 🔐 Настройки авторизации
SPOTIFY_CLIENT_ID = "f041013bac3d49d8a4e98c4a8a0b82e7"
SPOTIFY_CLIENT_SECRET = "4c0b9eb89ee64394a6aad4421b363c66"
SPOTIFY_REDIRECT_URI = "https://listen_link.railway.app/"
SPOTIFY_PLAYLIST_ID = "2KZDetQ5mkJxtizweC1f33"

# 🎧 Область доступа (scope)
scope = "playlist-modify-public playlist-read-private"

# ✅ Создание авторизованного клиента Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))


def search_tracks(title: str, artist: str, limit: int = 5) -> list[dict]:
    query = f"{title} {artist}"
    results = sp.search(q=query, type="track", limit=limit)
    tracks = results.get("tracks", {}).get("items", [])

    return [
        {
            "id": t["id"],
            "name": t["name"],
            "artist": ", ".join([a["name"] for a in t["artists"]]),
            "url": t["external_urls"]["spotify"]
        }
        for t in tracks
    ]


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
