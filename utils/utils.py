from datetime import datetime, timedelta
from typing import List


def yesterday_date_as_str() -> str:
    """Yesterday date as string in DD-MM-YYYY format."""
    return (datetime.today() - timedelta(days=1)).date().strftime('%d-%m-%Y')


def print_playlist_post_urls(urls: List[str]):
    """Print playlist post urls which have a VK playlist in the post."""
    if not urls:
        return
    print('\nPost urls which have a VK playlist:')
    for i, url in enumerate(urls, 1):
        print(f'{i}. {url}')
