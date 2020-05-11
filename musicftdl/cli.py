"""Console script for musicftdl."""
import sys
from typing import List

import click

from musicftdl.models import DownloadArgs
from musicftdl.musicftdl import download as dl
from musicftdl.musicftdl import (get_album_songs, get_singer_albums,
                                 get_song_info, get_song_url)
from musicftdl.musicftdl import search as search_kw
from musicftdl.utils import cut_str_to_multi_line, print_table


@click.group()
def cli():
    """A CLI tool to download music of Jay Chou and other singers with full song tags."""
    return 0


@cli.command()
# @click.option('-t', '--type', default='0', show_default=True,
#               type=click.Choice(['0', '2', '7', '8', '9', '12']),
#               help='0: song\n2: song list\n7: lyrics\n8: album\n9: singer\n12: mv')
@click.option('-P', '--page', default=1, show_default=True, help='Page No.')
@click.option('-S', '--page-size', default=20, show_default=True, help='Page size.')
@click.argument('keywords', nargs=-1)
def search(keywords, page, page_size):
    """Search songs by KEYWORDS."""
    try:
        result = search_kw(' '.join(keywords), page, page_size)
    except Exception as e:
        print(e)
        sys.exit(1)

    if result:
        headers = result[0].dict(exclude={'str_media_mid'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c  # noqa
                 for c in item.dict(exclude={'str_media_mid'}).values()]  # noqa
                for item in result]  # noqa

        print_table(headers, rows)


@cli.command()
@click.option('-P', '--page', default=1, show_default=True, help='Page No.')
@click.option('-S', '--page-size', default=50, show_default=True, help='Page size.')
@click.argument('mid')
def list(mid, page, page_size):
    """List albums/songs of the given SINGER/ALBUM MID."""
    try:
        result = get_singer_albums(mid, page, page_size)
    except Exception as e:
        print(e)
        sys.exit(1)

    if result:
        # for item in result:
        #     item.album_name = cut_str_to_multi_line(item.album_name, 12)
        headers = result[0].dict(exclude={'album_cover_url', 'album_cover_content',
                                          'songs', 'album_index', 'language'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c
                 for c in item.dict(exclude={'album_cover_url', 'album_cover_content',
                                             'songs', 'album_index', 'language'}).values()]
                for item in result]

        print_table(headers, rows)
        return

    try:
        result = get_album_songs(mid)
    except Exception as e:
        print(e)
        sys.exit(1)

    if result:
        headers = result[0].dict(exclude={'url', 'str_media_mid', 'genre'}).keys()
        rows = [['\n'.join(c) if isinstance(c, List) else c
                 for c in item.dict(exclude={'url', 'str_media_mid', 'genre'}).values()]
                for item in result]

        print_table(headers, rows)


@cli.command()
@click.argument('song-mid')
def show(song_mid):
    """Show information and play url of the given SONG MID."""
    try:
        song_info = get_song_info(song_mid)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not song_info.song_mid:
        print(f'Song <{song_mid}> not found!')
        sys.exit(1)

    intro = song_info.introduction
    if intro:
        song_info.introduction = cut_str_to_multi_line(intro, 50)
    headers = ['Category', 'Description']
    rows = [['\n'.join(c) if isinstance(c, List) else c for c in item]
            for item in song_info.dict(exclude={'url', 'str_media_mid', 'album_cover_url',
                                                'album_cover_content', 'album_singers_mid', 'album_singers_name'}).items()]
    print_table(headers, rows)
    try:
        print(get_song_url(song_mid))
    except Exception as e:
        print(e)


@cli.command()
@click.option('-s', '--singer', is_flag=True, help='Download songs by SINGER_MID.')
@click.option('-a', '--album', is_flag=True, help='Download songs by ALBUM_MID.')
@click.option('-k', '--keywords', is_flag=True, help='Download song by searching keywords.')
@click.option('-o', '--overwrite', is_flag=True, help='Overwrite exist files.')
@click.option('-d', '--destination', default='.', help='Destination to save songs.')
@click.option('-n', '--name-style', default='3', show_default=True,
              type=click.Choice(['1', '2', '3']),
              help='Style of filename. [ 1: SONG.ext | 2: SINGER - SONG.ext | 3: SINGER - ALBUM - SONG.ext')
@click.option('-t', '--album_types', default='SELO', show_default=True,
              help='Download songs of selected types of albums. [ S: Studio Album | '
                   'E: EP Single | L: Live Album | O: Others ]')
@click.option('-c/-C', '--classified/--no-classified', 'classified', default=True,
              show_default=True, help='Store in folders classify by singers and albums.')
@click.option('-f', '--format', default='128', show_default=True,
              type=click.Choice(['128', '320', 'm4a', 'flac', 'ape']), help='Song format.')
@click.option('-P', '--page', default=1, show_default=True, help='Page No.')
@click.option('-S', '--page-size', default=50, show_default=True, help='Page size.')
# @click.option('--proxy', default=None, help='Set a HTTP/HTTPS proxy, as format USERNAME:PASSWORD@IP:PORT.')
@click.argument('resource')
def download(**kwargs):
    """Download songs by SINGER/ALBUM MID or KEYWORDS."""
    args = DownloadArgs(**kwargs)
    try:
        dl(args)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
