from dataclasses import dataclass


@dataclass
class Track:
    """Track model."""
    artist: str
    name: str
    alternative_name: str
    vk_post_url: str = None

    @property
    def composed_full_name(self):
        """Compose full track name (artist name + track name)."""
        return f'{self.artist} {self.name}'

    @property
    def composed_alternative_full_name(self):
        """Compose alternative track name (artist name + alternative track name)."""
        return f'{self.artist} {self.alternative_name}'

    @property
    def not_found_name(self):
        """Compose full track name (artist name + track name) for a not found track."""
        return f'{self.artist} - {self.name}'
