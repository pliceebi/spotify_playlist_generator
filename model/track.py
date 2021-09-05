from dataclasses import dataclass
from typing import Dict


@dataclass
class Track:
    """Track model."""
    artist: str
    name: str
    alternative_name: str
    vk_post_url: str = None

    @classmethod
    def compose_artist_name(cls, artist_name: str) -> str:
        """Compose artist name."""
        if 'feat.' in artist_name:
            return artist_name.replace(' feat.', ',')
        return artist_name

    @classmethod
    def compose_full_name(cls, audio: Dict[str, str]) -> str:
        """Compose full track name."""
        title = audio['title']
        if subtitle := audio.get('subtitle'):
            return f'{title} {subtitle}'
        return title

    def get_composed_full_name(self) -> str:
        """Compose full track name (artist name + track name)."""
        return f'{self.artist} {self.name}'

    def get_composed_alternative_full_name(self) -> str:
        """Compose alternative track name (artist name + alternative track name)."""
        return f'{self.artist} {self.alternative_name}'

    def get_not_found_name(self) -> str:
        """Compose full track name (artist name + track name) for a not found track."""
        return f'{self.artist} - {self.name}'
