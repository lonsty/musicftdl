"""Console script for musicftdl."""
import math
import sys
from typing import List

import click

from musicftdl.models import DownloadArgs
from musicftdl.musicftdl import download as dl
from musicftdl.musicftdl import (get_album_songs, get_singer_albums,
                                 get_song_info, get_song_url)
from musicftdl.musicftdl import search as search_kw
from musicftdl.utils import print_table


@click.group()
def cli():
    return 0


@cli.command()
# @click.option('-t', '--type', default='0', show_default=True,
#               type=click.Choice(['0', '2', '7', '8', '9', '12']),
#               help='0: song\n2: song list\n7: lyrics\n8: album\n9: singer\n12: mv')
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
@click.option('-s', '--page-size', default=50, show_default=True, help='Page size.')
@click.argument('mid')
def list(mid, page, page_size):
    result = get_singer_albums(mid, page, page_size)
    if result:
        headers = result[0].dict(exclude={'album_cover_url', 'album_cover_content', 'songs'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c  # noqa
                 for c in item.dict(exclude={'album_cover_url', 'album_cover_content', 'songs'}).values()]  # noqa
                for item in result]  # noqa

        print_table(headers, rows)
        return

    result = get_album_songs(mid)
    if result:
        headers = result[0].dict(exclude={'url', 'str_media_mid'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c  # noqa
                 for c in item.dict(exclude={'url', 'str_media_mid'}).values()]  # noqa
                for item in result]  # noqa

        print_table(headers, rows)


@cli.command()
@click.argument('song-mid')
def show(song_mid):
    song_info = get_song_info(song_mid)
    if not song_info.song_mid:
        print(f'Song <{song_mid}> not found!')
        sys.exit(1)

    intro = song_info.introduction
    if intro:
        song_info.introduction = '\n'.join([intro[i * 50:(i + 1) * 50]
                                            for i in range(math.ceil(len(intro) / 50))])
    headers = ['Category', 'Description']
    rows = [['\n'.join(c) if isinstance(c, List) else c for c in item]
            for item in song_info.dict(exclude={'url', 'str_media_mid', 'album_cover_url',
                                                'album_cover_content'}).items()]
    print_table(headers, rows)
    print(get_song_url(song_mid))


@cli.command()
@click.option('-s', '--singer', is_flag=True, help='Download songs by SINGER_MID.')
@click.option('-a', '--album', is_flag=True, help='Download songs by ALBUM_MID.')
@click.option('-f', '--fuzzy', is_flag=True, help='Download song by fuzzy search.')
@click.option('-o', '--overwrite', is_flag=True, help='Overwrite exist files.')
@click.option('-d', '--destination', default='.', help='Destination to save songs.')
@click.option('-n', '--name-style', default='3', show_default=True,
              type=click.Choice(['1', '2', '3']),
              help='1: SONG.ext\n2: SINGER - SONG.ext\n3: SINGER - ALBUM - SONG.ext')
@click.option('-c/-C', '--classified/--no-classified', 'classified', default=True,
              show_default=True, help='Store in folders classify by singers and albums.')
@click.option('-F', '--format', default='128', show_default=True,
              type=click.Choice(['128', '320', 'm4a', 'flac', 'ape']), help='Song format.')
@click.option('-P', '--page', default=1, show_default=True, help='Page No.')
@click.option('-S', '--page-size', default=50, show_default=True, help='Page size.')
@click.argument('resource')
def download(**kwargs):
    args = DownloadArgs(**kwargs)
    try:
        dl(args)
    except Exception as e:
        print(e)
    return 0


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
