"""Main module."""
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import threading

from requests import Response, Session

from musicftdl.models import Consts, SearchResult, Singer, Album, Song

consts = Consts()
thread_local = threading.local()


def _get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = Session()
    return thread_local.session


def session_request(url: str, method: str='GET') -> Response:
    session = _get_session()
    with session.request(method, url, headers=consts.headers, timeout=consts.timeout) as resp:
        if resp.status_code != 200:
            raise Exception(resp.status_code)
    return resp


def search(key: str, limit: int=1) -> list:
    """
    Search by key, return by target

    :param key:
    :param target: 1 song, 2 album, 3 singer
    :return:
    """
    resp = session_request(consts.api.search.format(key, limit))

    result = []
    for item in resp.json().get('data', {}).get('list', []):
        result.append(SearchResult(
            singers_mid=[it.get('mid') for it in item.get('singer', {})],
            singers_name=[it.get('name') for it in item.get('singer', {})],
            album_name=item.get('albumname'),
            album_mid=item.get('albummid'),
            song_name=item.get('songname'),
            song_mid=item.get('songmid'),
            str_media_mid=item.get('strMediaMid')))
    return result


def get_albums(singer_mid: str, limit: int=50) -> list:
    resp = session_request(consts.api.singer_album.format(singer_mid, limit))

    result = []
    for idx, item in enumerate(reversed(resp.json().get('data', {}).get('list', []))):
        result.append(Album(
            album_mid=item.get('album_mid'),
            album_name=item.get('album_name'),
            album_type=item.get('albumtype'),
            Album_index=idx + 1,
            company=item.get('company', {}).get('company_name'),
            publish_time=item.get('pub_time'),
            singers_mid=[it.get('singer_mid') for it in item.get('singers', {})],
            singers_name=[it.get('singer_name') for it in item.get('singers', {})]))
    return result


def get_album_cover(album_mid: str):
    resp = session_request(consts.api.album.format(album_mid))

    return 'http' + resp.json().get('data', {}).get('picUrl')


def get_album_songs(album_mid: str) -> list:
    resp = session_request(consts.api.album_songs.format(album_mid))
    result = []

    for idx, item in enumerate(resp.json().get('data', {}).get('list', [])):
        result.append(Song(
            song_mid=item.get('mid'),
            song_name=item.get('name'),
            song_index=item.get('index_album'),
            singers_mid=[it.get('mid') for it in item.get('singer', {})],
            singers_name=[it.get('name') for it in item.get('singer', {})],
            str_media_mid=item.get('file', {}).get('media_mid')))
    return result


def get_song_url(song_mid: str, type: int='320') -> str:
    resp = session_request(consts.api.song_url.format(song_mid, type))
    return resp.json().get('data')


def main():
    result = search('周杰伦')[0]
    singer = Singer(singer_mid=result.singers_mid[0], singer_name=result.singer_name)

    singer.albums = get_albums(singer.singer_mid)
    for album in singer.albums:
        album.album_cover_url = get_album_cover(album.album_mid)
        album.songs = get_album_songs(album.album_mid)
        break
    for song in singer.albums[0].songs:
        song.url = get_song_url(song.song_mid)
    pass
