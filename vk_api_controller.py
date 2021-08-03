import requests
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

from model import Track


class Groups(Enum):
    """Enum for group domains."""
    JAZZVE = 'jazzve'
    SOUNDFIELDS = 'soundfields'
    GLBDOM = 'glbdom'
    RADIANT_SOUND = 'radiant_sound_home'


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
                'count': 50,
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

    def _process_post(self, post: Dict) -> List[Track]:
        """Process certain post."""
        tracks: List[Track] = []
        tracks_from_post = [attch['audio'] for attch in post['attachments'] if attch['type'] == 'audio']
        for track_from_post in tracks_from_post:
            artist = track_from_post['artist']
            full_name = self._compose_full_name(track_from_post)
            alternative_name = track_from_post['title']
            tracks.append(Track(artist, full_name, alternative_name))
        return tracks

    def _check_on_genres_condition(self, genres: List[str]) -> bool:
        """Return True if 'genres' have common substrings with 'self._desired_genres'. Otherwise, return False."""
        for genre in genres:
            for desired_genre in self._desired_genres:
                if desired_genre in genre:
                    return True
        return False

    def _process_soundfields(self) -> List[Track]:
        """Get all tracks from yesterday posts, which satisfy desired genres, from 'Soundfields' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.SOUNDFIELDS.value)
        tracks: List[Track] = []
        for post in yesterday_posts:
            genres = post['text'].split('\n')[-1].replace('#', '').split(' ')
            if not self._check_on_genres_condition(genres):
                continue
            tracks.extend(self._process_post(post))
        return tracks

    def _process_glbdom(self) -> List[Track]:
        """Get all tracks from yesterday posts from 'GLBDOM' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.GLBDOM.value)
        tracks = []
        for post in yesterday_posts:
            tracks.extend(self._process_post(post))
        return tracks

    def _process_radiant_sound(self) -> List[Track]:
        """Get all tracks from yesterday posts, which satisfy desired genres, from 'Radiant Sound' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.RADIANT_SOUND.value)
        tracks = []
        for post in yesterday_posts:
            genres = post['text'].split('\n')[1].split('/')
            if not self._check_on_genres_condition(genres):
                continue
            tracks.extend(self._process_post(post))
        return tracks

    def _process_jazzve(self) -> List[Track]:
        """Get all tracks from yesterday posts from 'JAZZVE Tubesbymates' VK group."""
        yesterday_posts = self._get_yesterday_posts(Groups.JAZZVE.value)
        tracks = []
        for post in yesterday_posts:
            tracks.extend(self._process_post(post))
        return tracks

    def process_groups(self) -> List[Track]:
        """Get yesterday tracks from all the groups presented in 'Groups' class."""
        posts: List[Track] = []
        # posts.extend(self._process_soundfields())
        # posts.extend(self._process_glbdom())
        posts.extend(self._process_radiant_sound())
        # posts.extend(self._process_jazzve())
        # Remove duplicates
        posts = list(set(posts))
        return posts


"""
Саммари по группам:
1) Soundfields отлично парсит. Нужно добавить обработку VA артистов
2) В jazzve надо парсить просто треки и все. Так как жанров там нет
3) Для glbdom то же самое, что и для jazzve
4) Radiant sound: вторая строка - жанры, перечисленные через /
"""
