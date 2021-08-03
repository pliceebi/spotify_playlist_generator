import requests
import json
from dataclasses import dataclass
from typing import List, Optional

from model import Track


@dataclass
class SpotifyAPIController:
    _user_id: str
    _api_token: str
    # _client_id: str
    # _client_secret: str
    # _api_token: str = None

    # def _request_token(self):
    #     url = 'https://accounts.spotify.com/api/token'
    #     response = requests.post(
    #         url=url,
    #         data={
    #             'grant_type': 'client_credentials',
    #             'client_id': self._client_id,
    #             'client_secret': self._client_secret
    #         }
    #     )
    #     status_code = response.status_code
    #     assert status_code == 200, f'Getting API token failed. Status code: {status_code}'
    #     self._api_token = response.json()['access_token']

    def create_playlist(self, playlist_name: str) -> str:
        """Create playlist with 'playlist_name' and return its id."""
        url = 'https://api.spotify.com/v1/users/{user_id}/playlists'
        response = requests.post(
            url=url.format(user_id=self._user_id),
            data=json.dumps(
                {
                    'name': playlist_name,
                    'description': 'Test',
                    'public': False,
                }
            ),
            headers={'Authorization': f'Bearer {self._api_token}'}
        )
        status_code = response.status_code
        assert status_code in (200, 201), (f'Playlist creation failed with status code: {status_code}.\n'
                                           f'Reason: {response.reason}')
        playlist_id = response.json()['id']
        return playlist_id

    def get_track_uri(self, name: str) -> Optional[str]:
        """Get Spotify track uri."""
        url = 'https://api.spotify.com/v1/search'
        response = requests.get(
            url=url,
            params={
                'q': name,
                'type': 'track'
            },
            headers={'Authorization': f'Bearer {self._api_token}'}
        )
        status_code = response.status_code
        assert status_code in (200, 201, 204), (f'Request to get track uri failed for {name} with status code: '
                                                f'{status_code}.\nReason: {response.reason}')
        tracks = response.json().get('tracks')
        if not tracks:
            return None

        items = tracks.get('items')
        if not items:
            return None
        # Get the best result from request
        return items[0]['uri']

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

    def add_tracks_to_playlist(self, playlist_id: str, tracks: List[Track]):
        """Add add tracks to the playlist."""
        for track in tracks:
            track_uri = self.get_track_uri(track.full_name)
            if not track_uri and track.alternative_name:
                track_uri = self.get_track_uri(track.full_name)
            if not track_uri:
                continue
            self.add_track_to_playlist(playlist_id, track_uri)

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
        playlist_length = response.json()['tracks']['total']
        return playlist_length
