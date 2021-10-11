import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import requests

from model.track import Track


class Groups(Enum):
    """Enum for group domains."""
    JAZZVE = 'jazzve'
    SOUNDFIELDS = 'soundfields'
    GLBDOM = 'glbdom'
    RADIANT_SOUND = 'radiant_sound_home'
    CRAFT_MUSIC = 'craftmusique'


class GroupsIDs(Enum):
    """Enum for group ids."""
    JAZZVE = 79069156
    SOUNDFIELDS = 5124202
    GLBDOM = 152579809
    RADIANT_SOUND = 32159054
    CRAFT_MUSIC = 40030199


@dataclass
class VKAPIController:
    _vk_api_token: str
    _api_version: float = 5.131
    _desired_genres: tuple = ('house', 'funk', 'disco', 'soul')

    @staticmethod
    def _check_date(post_date_ms: int) -> bool:
        """Check if the post was published yesterday. Otherwise, return False."""
        post_date = datetime.fromtimestamp(post_date_ms).date()
        yesterday_date = (datetime.today() - timedelta(days=1)).date()
        return post_date == yesterday_date

    def _request_posts(self, group_domain: str) -> List:
        """Send HTTP-request to VK API to get last 20 posts for 'group_domain'."""
        url = 'https://api.vk.com/method/wall.get'
        params: Dict[str, Union[int, str, float]] = {
            'domain': group_domain,
            'count': 20,
            'access_token': self._vk_api_token,
            'v': self._api_version
        }
        response = requests.get(url, params=params)
        assert response.status_code == 200, (f'Request failed to get posts from {group_domain} '
                                             f'with {response.status_code}. Reason: {response.reason}')
        return json.loads(response.text)['response']['items']

    @staticmethod
    def _compose_full_name(audio: Dict) -> str:
        """Compose full track name."""
        subtitle = audio.get('subtitle')
        title = audio['title']
        if subtitle:
            return f'{title} {subtitle}'
        return title

    def _get_yesterday_posts(self, group_domain: str) -> List[Dict]:
        """Get posts that were published yesterday for given VK 'group_domain'."""
        all_posts = self._request_posts(group_domain)
        yesterday_posts = [post for post in all_posts if self._check_date(post['date'])]
        return yesterday_posts

    # Not being used for now
    def _get_group_id(self, group_domain: str) -> int:
        """Get group id by its domain."""
        url = 'https://api.vk.com/method/utils.resolveScreenName'
        params: Dict[str, Union[float, str]] = {
            'screen_name': group_domain,
            'access_token': self._vk_api_token,
            'v': self._api_version
        }
        response = requests.get(url=url, params=params)
        assert response.status_code == 200
        return response.json()['response']['object_id']

    # Not being used for now
    def _get_post_url(self, group_id: int, post_id: int) -> str:
        """Get post url based on group and post ids."""
        url = 'https://api.vk.com/method/wall.getById'
        params: Dict[str, Union[str, float, List[str]]] = {
            'posts': [f'{group_id}_{post_id}'],
            'access_token': self._vk_api_token,
            'v': self._api_version
        }
        response = requests.get(url=url, params=params)
        return response.json()

    def _process_post(self, post: Dict, group_id: int) -> Tuple[List[Track], Optional[str]]:
        """Process a certain post."""
        tracks: List[Track] = []

        # if post is a repost
        if post.get('copy_history'):
            repost = post['copy_history'][0]
            if not repost.get('attachments'):
                return [], None
            tracks_from_post = [
                attch['audio'] for attch in repost['attachments'] if attch['type'] == 'audio'
            ]
        # just a usual post
        else:
            if not post.get('attachments'):
                return [], None
            tracks_from_post = [attch['audio'] for attch in post['attachments'] if attch['type'] == 'audio']
        # If there are no tracks in a post, it means that it is a VK-playlist which can't be parsed
        playlist_post_url = None
        if not tracks_from_post:
            playlist_post_url = f'vk.com/wall-{group_id}_{post["id"]}'

        for track_from_post in tracks_from_post:
            artist = Track.compose_artist_name(track_from_post['artist'])
            full_name = Track.compose_full_name(track_from_post)
            alternative_name = track_from_post['title']
            post_url = f'vk.com/wall-{group_id}_{post["id"]}'
            tracks.append(Track(artist, full_name, alternative_name, post_url))
        return tracks, playlist_post_url

    def _check_genres(self, post_genres: List[str]) -> bool:
        """Check if post genres intersect with desired genres."""
        if set(post_genres).intersection(self._desired_genres):
            return True
        return False

    def process_groups(self) -> Tuple[List[Track], List[str]]:
        """
        Process all yesterday posts in all groups presented in Groups class.

        -------
        Returns
            Tuple[List[Track], List[str]]
            First element of tuple is a list of yesterday tracks from all the groups presented in
            'Groups' class.
            Second element of tuple is a list of VK urls which consists of playlists which can't be parsed.
        """
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for group in Groups:
            yesterday_posts = self._get_yesterday_posts(group.value)
            for post in yesterday_posts:

                if group is Groups.RADIANT_SOUND:
                    if not post.get('text'):
                        continue
                    genres = post['text'].split('\n')[1].split('/')
                    if not self._check_genres(genres):
                        continue

                if group is Groups.SOUNDFIELDS:
                    if post['text'] not in ('#somegoods', '#qweektunes'):
                        genres = post['text'].split('\n')[-1].replace('#', '').split(' ')
                        if not self._check_genres(genres):
                            continue

                found_tracks, playlist_post_url = self._process_post(post, GroupsIDs[group.name].value)
                tracks.extend(found_tracks)

                if playlist_post_url:
                    playlist_post_urls.append(playlist_post_url)

        return tracks, playlist_post_urls
