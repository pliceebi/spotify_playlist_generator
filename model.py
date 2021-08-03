from dataclasses import dataclass


@dataclass
class Track:
    """Track model."""
    artist: str
    full_name: str
    alternative_name: str = None
    post_url: str = None
