import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def check_created(playlists: dict, new_name: str) -> bool:
    for item in playlists['items']:
        if item['name'] == new_name:
            return True
    return False


def find_id(playlists: dict, name: str) -> str:
    for item in playlists['items']:
        if item['name'] == name:
            return item['id']


config = configparser.ConfigParser()
config.read('config.cfg')
c_id = config.get('SPOTIFY', 'CLIENT_ID')
c_secret = config.get('SPOTIFY', 'CLIENT_SECRET')
sc = "user-library-read user-top-read playlist-modify-public"
uri = "http://localhost:8080/"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=c_id, client_secret=c_secret, redirect_uri=uri, scope=sc))

# liked = sp.current_user_saved_tracks()
# # print(liked)
# for idx, item in enumerate(liked['items']):
#     track = item['track']
#     print(idx + 1, track['artists'][0]['name'], " – ", track['name'])
#
# print()
# popular = sp.current_user_top_tracks()
# # print(popular)
# for idx, item in enumerate(popular['items']):
#     # print(item)
#     track = item['album']
#     print(idx + 1, track['artists'][0]['name'], " – ", track['name'])

play_name = ''
while not check_created(sp.current_user_playlists(), play_name):
    play_name = input("Enter a playlist to search: ")

myself = sp.me()['id']
new_name = play_name + ' ∩ Liked Songs'
playlists = sp.current_user_playlists()

if not check_created(playlists, new_name):
    sp.user_playlist_create(myself, new_name, collaborative=False, description='spotipy test')

new_id = find_id(sp.current_user_playlists(), new_name)
play_id = find_id(sp.current_user_playlists(), play_name)
play = sp.playlist_tracks(play_id)
songs_left = play['total']

sp.playlist_replace_items(new_id, '')

iter = 0
ids_in_both = []
while songs_left > 0:
    play = sp.playlist_tracks(play_id, offset=100 * iter)
    for item in play['items']:
        id = item['track']['id']
        if id is not None and sp.current_user_saved_tracks_contains([id])[0]:
            ids_in_both.append(id)
            print("#" + str(len(ids_in_both)) + " Song in both: " + item['track']['name'])
        songs_left -= 1
    iter += 1

print("\n" + str(len(ids_in_both)) + " songs in both playlists")
print("Adding songs...\n")
for id in ids_in_both:
    sp.playlist_add_items(new_id, items=[id])
print("Done")
