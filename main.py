import os

from core.spotify_api_controller import SpotifyAPIController
from core.vk_api_controller import VKAPIController
from utils.utils import print_playlist_post_urls


def main():
    # Init ProcessVkGroups object
    vk_token = os.environ.get('VK_API_TOKEN')
    vk = VKAPIController(vk_token)

    # Get tracks and playlist post urls from VK
    tracks, playlist_post_urls = vk.process_groups()
    num_of_tracks_to_find = len(tracks)

    if not num_of_tracks_to_find:
        print('Nothing to find today :(')
        print_playlist_post_urls(playlist_post_urls)
        return

    # Init SpotifyAPIController object
    user_id = os.environ.get('SPOTIFY_USER_ID')
    spotify_api_token = os.environ.get('SPOTIFY_MY_TOKEN')
    spotify = SpotifyAPIController(user_id, spotify_api_token)

    # Create the playlist in Spotify and add tracks to it
    playlist_id = spotify.create_playlist()
    not_found_tracks = spotify.add_tracks_to_playlist(playlist_id, tracks)
    num_of_found_tracks = spotify.get_length_of_playlist(playlist_id)

    print(f'Number of tracks to find: {num_of_tracks_to_find}. '
          f'Number of found tracks: {num_of_found_tracks}')

    if num_of_found_tracks:
        print(f'Percentage of found tracks from VK in Spotify: '
              f'{round(num_of_found_tracks / num_of_tracks_to_find * 100, 1)}%')
    else:
        print('Percentage of found tracks from VK in Spotify: 0%')

    if not_found_tracks:
        print('\nTrack which have not been found in Spotify:')
        for i, (post_url, tracks) in enumerate(not_found_tracks.items(), 1):
            tracks = '\n'.join(tracks)
            print(f"{i}. {post_url}"
                  f"\n{tracks}")

    print_playlist_post_urls(playlist_post_urls)


if __name__ == '__main__':
    main()
