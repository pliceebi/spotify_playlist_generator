import os

from vk_api_controller import VKAPIController
from spotify_api_controller import SpotifyAPIController
from utils import yesterday_date_as_str


# TODO
# 1) What to do with unfound tracks?
# 2) Remove duplicates
# 3) Rework 'Radiant Sound', 'Sounfields' and 'Jazzve'


def main():
    # Init ProcessVkGroups object
    vk_token = os.environ.get('VK_API_TOKEN')
    vk = VKAPIController(vk_token)

    # Get tracks from VK
    tracks = vk.process_groups()
    num_of_tracks_to_find = len(tracks)

    if not num_of_tracks_to_find:
        print('Nothing to find today :(')
        return

    # Init SpotifyAPIController object
    user_id = os.environ.get('SPOTIFY_USER_ID')
    spotify_api_token = os.environ.get('SPOTIFY_MY_TOKEN')
    spotify = SpotifyAPIController(user_id, spotify_api_token)

    # Create the playlist in Spotify and add tracks to it
    playlist_name = f'Tracks from {yesterday_date_as_str()}'
    playlist_id = spotify.create_playlist(playlist_name)
    spotify.add_tracks_to_playlist(playlist_id, tracks)
    num_of_found_tracks = spotify.get_length_of_playlist(playlist_id)

    print(f'Number of tracks to find: {num_of_tracks_to_find}. Number of found tracks: {num_of_found_tracks}')
    if num_of_found_tracks:
        print(f'Percentage of found tracks from VK in Spotify: {num_of_found_tracks / num_of_tracks_to_find * 100}%')
    else:
        print('Percentage of found tracks from VK in Spotify: 0%')


if __name__ == '__main__':
    main()
