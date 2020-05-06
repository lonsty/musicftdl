"""Console script for musicftdl."""
import sys
from typing import List

import click

from musicftdl.utils import print_table

from musicftdl.musicftdl import search as search_kw, get_albums, get_album_songs, get_song_url, get_song_info, download_music, add_tags, get_album_cover

# List = list

@click.group()
def cli():
    return 0


@cli.command()
@click.option('-p', '--page', default=1, show_default=True, help='Page No.')
@click.option('-s', '--page-size', default=20, show_default=True, help='Page size.')
@click.argument('keywords', nargs=-1)
def search(keywords, page, page_size):
    result = search_kw(' '.join(keywords), page, page_size)
    if result:
        headers = result[0].dict(exclude={'str_media_mid'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c  # noqa
                 for c in item.dict(exclude={'str_media_mid'}).values()]  # noqa
                for item in result]  # noqa

        print_table(headers, rows)


@cli.command()
@click.option('-p', '--page', default=1, show_default=True, help='Page No.')
@click.option('-s', '--page-size', default=20, show_default=True, help='Page size.')
@click.argument('mid')
def list(mid, page, page_size):
    result = get_albums(mid, page, page_size) or get_album_songs(mid)
    if result:
        headers = result[0].dict().keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c  # noqa
                 for c in item.dict().values()]  # noqa
                for item in result]  # noqa

        print_table(headers, rows)


@cli.command()
@click.argument('mid')
def show(mid):
    song_info = get_song_info(mid)
    headers = ['Category', 'Description']
    rows = [['\n'.join(c) if isinstance(c, List) else c for c in item] for item in song_info.dict().items()]
    print_table(headers, rows)
    print(get_song_url(mid))


@cli.command()
@click.option('-s', '--singer', is_flag=True, help='')
@click.option('-a', '--album', is_flag=True, help='')
@click.option('-f', '--fuzzy', is_flag=True, help='')
@click.option('-d', '--destination', default='.', help='')
@click.option('-n', '--name-style', default=3, help='')
@click.option('-c/-C', '--classified/--no-classified', 'classified', default=True, help='')
@click.argument('resource')
def download(**kwargs):
    # TODO
    song_info = get_song_info(mid)
    url = get_song_url(mid)
    cover_url = get_album_cover(song_info.album_mid)
    filename = f'{song_info.singer_name} - {song_info.album_name} - {song_info.song_name}.mp3'
    download_music(url, filename)
    add_tags(filename, song_info, cover_url)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
