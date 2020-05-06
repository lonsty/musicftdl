"""Main module."""
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import threading

import eyed3
from requests import Response, Session

from musicftdl.models import Consts, SearchResult, Singer, Album, Song, SongInfo, DownloadArgs

consts = Consts()
thread_local = threading.local()
eyed3.log.setLevel("ERROR")


def _get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = Session()
    return thread_local.session


def session_request(url: str, method: str='GET') -> Response:
    session = _get_session()
    with session.request(method, url, headers=consts.headers, timeout=consts.timeout) as resp:
        resp.raise_for_status()
    return resp


def search(key: str, page: int=1, page_size: int=10) -> list:
    """
    Search by key, return by target

    :param key:
    :param target: 1 song, 2 album, 3 singer
    :return:
    """
    resp = session_request(consts.api.search.format(key, page, page_size))

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


def get_albums(singer_mid: str, page: int=1, page_size: int=50) -> list:
    resp = session_request(consts.api.singer_album.format(singer_mid, page, page_size))

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

    return 'http:' + resp.json().get('data', {}).get('picUrl')


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


def get_song_info(song_mid: str) -> SongInfo:
    resp = session_request(consts.api.song_info.format(song_mid))
    data = resp.json().get('data', {})
    song_info = SongInfo(
        song_mid=data.get('track_info', {}).get('mid', {}),
        song_name=data.get('track_info', {}).get('name', {}),
        singers_mid=[it.get('mid') for it in data.get('track_info', {}).get('singer', {})],
        singers_name=[it.get('name') for it in data.get('track_info', {}).get('singer', {})],
        album_mid=data.get('track_info', {}).get('album', {}).get('mid'),
        album_name=data.get('track_info', {}).get('album', {}).get('name'),
        song_index=data.get('track_info', {}).get('index_album'),
        company=data.get('info', {}).get('company', {}).get('content', {})[0].get('value'),
        genre=data.get('info', {}).get('genre', {}).get('content', {})[0].get('value'),
        introduction=data.get('info', {}).get('intro', {}).get('content', {})[0].get('value'),
        language=data.get('info', {}).get('lan', {}).get('content', {})[0].get('value'),
        publish_time=data.get('info', {}).get('pub_time', {}).get('content', {})[0].get('value'),
    )

    return song_info


def download_music(url: str, filename: str):
    with open(filename, 'wb') as f:
        for chunk in session_request(url).iter_content(8192):
            f.write(chunk)
    add_tags()


def add_tags(filename: str, song: SongInfo, cover: str):
    # with eyed3.load(filename) as audiofile:
    audiofile = eyed3.load(filename)

    audiofile.tag.album = song.album_name
    audiofile.tag.album_artist = song.singer_name
    # audiofile.tag.album_type = song.genre

    audiofile.tag.title = song.song_name
    audiofile.tag.artist = song.singer_name

    audiofile.tag.track_num = (song.song_index, 0)
    audiofile.tag.disc_num = (None, None)
    audiofile.tag.publisher = song.company
    audiofile.tag.copyright = song.company

    audiofile.tag.recording_date = song.publish_date
    audiofile.tag.release_date = song.publish_time
    # audiofile.tag.best_release_date = song.publish_date

    with session_request(cover) as resp:
        audiofile.tag.images.set(3, resp.content, 'image/jepg', song.album_name)

    audiofile.tag.save(encoding='utf-8')


def main(**kwargs):
    args = DownloadArgs(**kwargs)
    pool = ThreadPoolExecutor(max_workers=20)
    album_songs_futures = {}
    album_cover_url_futures = {}
    album_cover_content_futures = {}
    song_url_futures = {}
    song_content_futures = {}

    if args.fuzzy:
        result = search(args.resource, page=1, page_size=1)
        assert result, f'Resource <{args.resource}> not found!'

        singer = Singer(singer_mid=result[0].singers_mid[0], singer_name=result[0].singer_name)

        singer.albums = get_albums(singer.singer_mid)

        # TODO
        album_songs_futures = {pool.submit(get_album_songs, album.album_mid): album for album in singer.albums}
        album_cover_url_futures = {pool.submit(get_album_cover, album.album_mid): album for album in singer.albums}

        for future in as_completed(album_cover_url_futures):
            try:
                result = future.result()
            except Exception:
                pass
            else:
                album = album_cover_url_futures[future]
                album.album_cover_url = result
                album_cover_content_futures[pool.submit(session_request, result)] = album


        for future in as_completed(album_songs_futures):
            try:
                result = future.result()
            except Exception:
                pass
            else:
                album = album_songs_futures[future]
                album.songs = result
                for song in result:
                    song_url_futures[pool.submit(get_song_url, song.song_mid)] = song


        for future in as_completed(album_cover_content_futures):
            try:
                result = future.result()
            except Exception:
                pass
            else:
                album_cover_content_futures[future].album_cover_content = result


        for future in as_completed(song_url_futures):
            try:
                result = future.result()
            except Exception:
                pass
            else:
                song = song_url_futures[future]
                song.url = result
                song_content_futures[pool.submit(download_music(result, args.format_name(song)))] = song

        # TODO



        for album in singer.albums:
            album.album_cover_url = get_album_cover(album.album_mid)
            album.songs = get_album_songs(album.album_mid)
            break
        for song in singer.albums[0].songs:
            song.url = get_song_url(song.song_mid)
        pass
