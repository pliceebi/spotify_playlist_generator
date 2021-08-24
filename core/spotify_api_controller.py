import requests
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from base64 import b64encode

from model.track import Track
from utils.utils import yesterday_date_as_str


@dataclass
class SpotifyAPIController:
    _user_id: str
    _api_token: str
    # _client_id: str
    # _client_secret: str
    # _api_token: str = None

    def create_playlist(self) -> str:
        """Create playlist with 'playlist_name' and return its id."""
        playlist_name = f'Tracks from {yesterday_date_as_str()}'
        url = 'https://api.spotify.com/v1/users/{user_id}/playlists'
        response = requests.post(
            url=url.format(user_id=self._user_id),
            data=json.dumps(
                {
                    'name': playlist_name,
                    'public': False,
                }
            ),
            headers={'Authorization': f'Bearer {self._api_token}'}
        )
        status_code = response.status_code
        assert status_code in (200, 201), (f'Playlist creation failed with status code: {status_code} \n'
                                           f'Reason: {response.reason}')
        playlist_id = response.json()['id']
        return playlist_id

    def get_track_uri(self, composed_full_name: str, track_name: str) -> Optional[str]:
        """Get Spotify track uri."""
        url = 'https://api.spotify.com/v1/search'
        response = requests.get(
            url=url,
            params={
                'q': composed_full_name,
                'type': 'track'
            },
            headers={'Authorization': f'Bearer {self._api_token}'}
        )
        status_code = response.status_code
        assert status_code in (200, 201, 204), (f'Request to get track uri failed for {composed_full_name} '
                                                f'with status code: {status_code}.\n'
                                                f'Reason: {response.reason}')
        tracks = response.json().get('tracks')
        if not tracks:
            return None

        items = tracks.get('items')
        if not items:
            return None

        for item in items:
            if item['name'].replace('- ', '') == track_name:
                return item['uri']
        return None

    def add_track_to_playlist(self, playlist_id: str, track_uri: str):
        """Add track by track uri to playlist by its id."""
        url = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        response = requests.post(
            url=url.format(playlist_id=playlist_id),
            data=json.dumps({'uris': [track_uri]}),
            headers={'Authorization': f'Bearer {self._api_token}', 'Content-Type': 'application/json'}
        )
        status_code = response.status_code
        assert status_code in (200, 201), (f'Adding tracks to the playlist failed with status code: {status_code}.\n'
                                           f'Reason: {response.reason}')

    def add_tracks_to_playlist(self, playlist_id: str, tracks: List[Track]) -> Dict[str, List[str]]:
        """
        Add tracks to the playlist if they are not in the playlist yet.

        And return names of tracks which have not been found in Spotify.
        """
        added_tracks_uris = []
        not_found_tracks = {}
        for track in tracks:
            track_uri = self.get_track_uri(track.composed_full_name, track.name)
            if not track_uri:
                if track.vk_post_url not in not_found_tracks.keys():
                    not_found_tracks[track.vk_post_url] = [track.not_found_name]
                else:
                    not_found_tracks[track.vk_post_url].append(track.not_found_name)
                continue
            if track_uri not in added_tracks_uris:
                self.add_track_to_playlist(playlist_id, track_uri)
                added_tracks_uris.append(track_uri)
        return not_found_tracks

    def get_length_of_playlist(self, playlist_id: str) -> int:
        """Get number of tracks in the playlist."""
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        response = requests.get(
            url=url.format(playlist_id=playlist_id),
            headers={'Authorization': f'Bearer {self._api_token}', 'Content-Type': 'application/json'}
        )
        status_code = response.status_code
        assert status_code in (200, 201), (f'Getting the playlist items failed with status code: {status_code}.\n'
                                           f'Reason: {response.reason}')
        playlist_length = response.json()['total']
        return playlist_length
