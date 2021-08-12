import requests
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

from model import Track


class Groups(Enum):
    """Enum for group domains."""
    JAZZVE = 'jazzve'
    SOUNDFIELDS = 'soundfields'
    GLBDOM = 'glbdom'
    RADIANT_SOUND = 'radiant_sound_home'
    # CRAFT_MUSIC = 'craftmusique'


class GroupsIDs(Enum):
    """Enum for group ids."""
    JAZZVE = 79069156
    SOUNDFIELDS = 5124202
    GLBDOM = 152579809
    RADIANT_SOUND = 32159054
    # CRAFT_MUSIC = 40030199


@dataclass
class VKAPIController:
    _vk_api_token: str
    _api_version: float = 5.131

    # TODO: replace with attribute with default (but how?)
    @property
    def _desired_genres(self) -> set:
        return {'house', 'funk', 'disco', 'soul'}

    @staticmethod
    def _check_date(post_date_ms: int) -> bool:
        """Check if post was published yesterday. Otherwise, return False."""
        post_date = datetime.fromtimestamp(post_date_ms).date()
        yesterday_date = (datetime.today() - timedelta(days=1)).date()
        return post_date == yesterday_date

    def _request_posts(self, group_domain: str) -> Dict:
        """Send HTTP-request to VK API to get last 20 posts for 'group_domain'."""
        url = 'https://api.vk.com/method/wall.get'
        response = requests.get(
            url,
            params={
                'domain': group_domain,
                'count': 20,
                'access_token': self._vk_api_token,
                'v': self._api_version
            }
        )
        assert response.status_code == 200, (f'Request failed to get posts from {group_domain} '
                                             f'with {response.status_code}. Reason: {response.reason}')
        return json.loads(response.text)

    @staticmethod
    def _compose_full_name(audio: Dict) -> str:
        """Compose full track name."""
        subtitle = audio.get('subtitle')
        title = audio['title']
        if subtitle:
            return f'{title} {subtitle}'
        return title

    def _get_yesterday_posts(self, group_domain: str) -> List:
        """Get posts that were published yesterday for given VK 'group_domain'."""
        all_posts = self._request_posts(group_domain)
        yesterday_posts = [post for post in all_posts['response']['items'] if self._check_date(post['date'])]
        return yesterday_posts

    # Not being used for now
    def _get_group_id(self, group_domain: str) -> int:
        """Get group id by its domain."""
        url = 'https://api.vk.com/method/utils.resolveScreenName'
        response = requests.get(
            url=url,
            params={
                'screen_name': group_domain,
                'access_token': self._vk_api_token,
                'v': self._api_version
            }
        )
        assert response.status_code == 200
        return response.json()['response']['object_id']

    # Not being used for now
    def _get_post_url(self, group_id: int, post_id: int) -> str:
        """Get post url based on group and post ids."""
        url = 'https://api.vk.com/method/wall.getById'
        response = requests.get(
            url=url,
            params={
                'posts': [f'{group_id}_{post_id}'],
                'access_token': self._vk_api_token,
                'v': self._api_version
            }
        )
        return response.json()

    def _process_post(self, post: Dict, group_id: str) -> Tuple[List[Track], Optional[str]]:
        """Process certain post."""
        tracks: List[Track] = []

        tracks_from_post = [attch['audio'] for attch in post['attachments'] if attch['type'] == 'audio']
        # If there are no tracks in a post, it means it is a VK-playlist which can't be parsed
        playlist_post_url = None
        if not tracks_from_post:
            playlist_post_url = f'vk.com/wall-{group_id}_{post["id"]}'

        for track_from_post in tracks_from_post:
            artist = track_from_post['artist']
            full_name = self._compose_full_name(track_from_post)
            alternative_name = track_from_post['title']
            tracks.append(Track(artist, full_name, alternative_name))
        return tracks, playlist_post_url

    def _check_on_genres_condition(self, genres: List[str]) -> bool:
        """Return True if 'genres' have common genres with 'desired_genres'. Otherwise, return False."""
        for genre in genres:
            for desired_genre in self._desired_genres:
                if desired_genre in genre:
                    return True
        return False

    # Not being used for now
    def _process_soundfields(self) -> Tuple[List[Track], List[str]]:
        """Get all tracks from yesterday posts, which satisfy desired genres, from 'Soundfields' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.SOUNDFIELDS.value)
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for post in yesterday_posts:
            genres = post['text'].split('\n')[-1].replace('#', '').split(' ')
            if not self._check_on_genres_condition(genres):
                continue
            found_tracks, playlist_post_url = self._process_post(post, GroupsIDs.SOUNDFIELDS.value)
            tracks.extend(found_tracks)
            if playlist_post_url:
                playlist_post_urls.append(playlist_post_url)
        return tracks, playlist_post_urls

    # Not being used for now
    def _process_glbdom(self) -> Tuple[List[Track], List[str]]:
        """Get all tracks from yesterday posts from 'GLBDOM' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.GLBDOM.value)
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for post in yesterday_posts:
            found_tracks, playlist_post_url = self._process_post(post, GroupsIDs.GLBDOM.value)
            tracks.extend(found_tracks)
            if playlist_post_url:
                playlist_post_urls.append(playlist_post_url)
        return tracks, playlist_post_urls

    # Not being used for now
    def _process_radiant_sound(self) -> Tuple[List[Track], List[str]]:
        """Get all tracks from yesterday posts, which satisfy desired genres, from 'Radiant Sound' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.RADIANT_SOUND.value)
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for post in yesterday_posts:
            genres = post['text'].split('\n')[1].split('/')
            if not self._check_on_genres_condition(genres):
                continue
            found_tracks, playlist_post_url = self._process_post(post, GroupsIDs.RADIANT_SOUND.value)
            tracks.extend(found_tracks)
            if playlist_post_url:
                playlist_post_urls.append(playlist_post_url)
        return tracks, playlist_post_urls

    # Not being used for now
    def _process_jazzve(self) -> Tuple[List[Track], List[str]]:
        """Get all tracks from yesterday posts from 'JAZZVE Tubesbymates' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.JAZZVE.value)
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for post in yesterday_posts:
            found_tracks, playlist_post_url = self._process_post(post, GroupsIDs.JAZZVE.value)
            tracks.extend(found_tracks)
            if playlist_post_url:
                playlist_post_urls.append(playlist_post_url)
        return tracks, playlist_post_urls

    def process_groups(self) -> Tuple[List[Track], List[str]]:
        """
        Process all yesterday posts in all groups presented in Groups class.

        -------
        Returns
            Tuple[List[Track], List[str]]
            First element of tuple is a list of yesterday tracks from all the groups presented in 'Groups' class.
            Second element of tuple is a list of VK urls which consists of playlists which can't be parsed.
        """
        tracks: List[Track] = []
        playlist_post_urls: List[str] = []
        for group in Groups:
            yesterday_posts = self._get_yesterday_posts(group.value)
            for post in yesterday_posts:

                if group is Groups.RADIANT_SOUND:
                    genres = post['text'].split('\n')[1].split('/')
                    if not self._check_on_genres_condition(genres):
                        continue

                if group is Groups.SOUNDFIELDS:
                    if not post['text'] == '#somegoods':
                        genres = post['text'].split('\n')[-1].replace('#', '').split(' ')
                        if not self._check_on_genres_condition(genres):
                            continue

                found_tracks, playlist_post_url = self._process_post(post, GroupsIDs[group.name].value)
                tracks.extend(found_tracks)
                if playlist_post_url:
                    playlist_post_urls.append(playlist_post_url)

        # Remove duplicates
        # tracks = list(set(tracks))
        return tracks, playlist_post_urls


"""
Саммари по группам:
1) Soundfields отлично парсит. Нужно добавить обработку VA артистов
2) В jazzve надо парсить просто треки и все. Так как жанров там нет
3) Для glbdom то же самое, что и для jazzve
4) Radiant sound: вторая строка - жанры, перечисленные через /
"""
