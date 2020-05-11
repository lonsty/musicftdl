"""Main module."""
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from typing import List

import eyed3
from requests import Response, Session, exceptions

from musicftdl.id3_genres import Genre
from musicftdl.models import (Album, Consts, DownloadArgs, SearchResult,
                              Singer, Song, SongInfo)
from musicftdl.utils import retry

consts = Consts()
thread_local = threading.local()
eyed3.log.setLevel("ERROR")


def _get_session() -> Session:
    """
    Get a instance of requests.Session
    :return: requests.Session
    """
    if not hasattr(thread_local, "session"):
        thread_local.session = Session()
    return thread_local.session


class DataNotFoundError(Exception):
    pass


@retry(Exception)
def session_request(url: str, method: str='GET') -> Response:
    session = _get_session()

    with session.request(method, url, headers=consts.headers, timeout=consts.timeout) as resp:
        resp.raise_for_status()
        return resp


def get_json_data(resp):
    try:
        res = resp.json()
    except Exception as e:
        print(e)
        return {}
    else:
        if res.get('result') != 100:
            raise DataNotFoundError(res.get('errMsg'))
        data = res.get('data')
        if not data:
            raise DataNotFoundError('Data is empty')
        return data


def search(key: str, page: int=1, page_size: int=20) -> List[SearchResult]:
    data = get_json_data(session_request(consts.api.search.format(key, page, page_size)))

    result = []
    for item in data.get('list', []):
        result.append(SearchResult(
            singers_mid=[it.get('mid') for it in item.get('singer', [{}])],
            singers_name=[it.get('name') for it in item.get('singer', [{}])],
            album_name=item.get('albumname'),
            album_mid=item.get('albummid'),
            song_name=item.get('songname'),
            song_mid=item.get('songmid'),
            duration=item.get('interval'),
            str_media_mid=item.get('strMediaMid', '')
        ))
    return result


def get_singer_albums(singer_mid: str, page: int=1, page_size: int=50) -> List[Album]:
    data = get_json_data(session_request(consts.api.singer_album.format(singer_mid, page, page_size)))

    result = []
    for idx, item in enumerate(reversed(data.get('list', []))):
        result.append(Album(
            album_mid=item.get('album_mid'),
            album_name=item.get('album_name'),
            album_type=item.get('albumtype'),
            album_index=idx + 1,
            language=item.get('lan'),
            song_count=item.get('latest_song', {}).get('song_count'),
            company=item.get('company', {}).get('company_name'),
            publish_time=item.get('pub_time'),
            singers_mid=[it.get('singer_mid') for it in item.get('singers', [{}])],
            singers_name=[it.get('singer_name') for it in item.get('singers', [{}])]
        ))
    return result


def get_album(album_mid: str) -> Album:
    data = get_json_data(session_request(consts.api.album.format(album_mid)))

    album = Album(
        album_mid=data.get('mid'),
        album_name=data.get('name'),
        album_type=None,
        album_index=None,
        company=data.get('company'),
        publish_time=data.get('publishTime'),
        singers_mid=[it.get('mid') for it in data.get('ar', [{}])],
        singers_name=[it.get('name') for it in data.get('ar', [{}])],
        album_cover_url=data.get('picUrl')
    )
    return album


def get_album_cover(album_mid: str) -> str:
    data = get_json_data(session_request(consts.api.album.format(album_mid)))

    return 'http:' + data.get('picUrl')


def get_album_songs(album_mid: str) -> List[Song]:
    data = get_json_data(session_request(consts.api.album_songs.format(album_mid)))
    result = []

    for idx, item in enumerate(data.get('list', [])):
        result.append(Song(
            song_mid=item.get('mid'),
            song_name=item.get('name'),
            song_index=item.get('index_album'),
            singers_mid=[it.get('mid') for it in item.get('singer', [{}])],
            singers_name=[it.get('name') for it in item.get('singer', [{}])],
            duration=item.get('interval'),
            genre=item.get('genre'),
            str_media_mid=item.get('file', {}).get('media_mid')
        ))
    return result


def get_song_url(song_mid: str, format: str= '128') -> str:
    return get_json_data(session_request(consts.api.song_url.format(song_mid, format)))


def get_song_info(song_mid: str) -> SongInfo:
    data = get_json_data(session_request(consts.api.song_info.format(song_mid)))
    song_info = SongInfo(
        song_mid=data.get('track_info', {}).get('mid'),
        song_name=data.get('track_info', {}).get('name'),
        duration=data.get('track_info', {}).get('interval'),
        singers_mid=[it.get('mid') for it in data.get('track_info', {}).get('singer', [{}])],
        singers_name=[it.get('name') for it in data.get('track_info', {}).get('singer', [{}])],
        album_mid=data.get('track_info', {}).get('album', {}).get('mid'),
        album_name=data.get('track_info', {}).get('album', {}).get('name'),
        song_index=data.get('track_info', {}).get('index_album'),
        company=data.get('info', {}).get('company', {}).get('content', [{}])[0].get('value'),
        genre=Genre.get_num(data.get('info', {}).get('genre', {}).get('content', [{}])[0].get('value')),
        introduction=data.get('info', {}).get('intro', {}).get('content', [{}])[0].get('value'),
        language=data.get('info', {}).get('lan', {}).get('content', [{}])[0].get('value'),
        publish_time=data.get('info', {}).get('pub_time', {}).get('content', [{}])[0].get('value')
    )
    return song_info


def download_music(url: str, filename: str, overwrite: bool=False):
    if os.path.isfile(filename) \
        and not overwrite \
        and os.path.getsize(filename) > 0:
        print(f'{filename} [Skipped]')
        return False

    try:
        resp = session_request(url)
    except Exception as e:
        print(e)
    else:
        if resp is not None:
            with open(filename, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            print(filename)
            return True


def add_tags(filename: str, song_info: SongInfo):
    try:
        audiofile = eyed3.load(filename)

        audiofile.tag.title = song_info.song_name
        audiofile.tag.artist = song_info.singer_name
        # audiofile.tag.genre = song_info.genre
        audiofile.tag.album = song_info.album_name
        audiofile.tag.album_artist = song_info.album_singer_name
        # audiofile.tag.album_type = song.genre
        audiofile.tag.track_num = (song_info.song_index, 0)
        # audiofile.tag.disc_num = (None, None)
        audiofile.tag.publisher = song_info.company
        audiofile.tag.copyright = song_info.company
        audiofile.tag.recording_date = song_info.publish_date
        audiofile.tag.release_date = song_info.publish_time
        # audiofile.tag.best_release_date = song.publish_date
        audiofile.tag.images.set(3, song_info.album_cover_content, 'image/jpeg', song_info.album_name + '.JPG')
        audiofile.tag.save(encoding='utf-8')
    except Exception:
        pass


def download_with_tags(filename: str, song_info: SongInfo, overwrite: bool=False, retag: bool=True):
    downloaded = download_music(song_info.url, filename, overwrite)
    if downloaded and retag:
        add_tags(filename, song_info)


def fetch_album_chore(album: Album, args: DownloadArgs) -> Album:
    with ThreadPoolExecutor(max_workers=20) as pool:
        album.songs = get_album_songs(album.album_mid)
        song_url_futures = {pool.submit(get_song_url, song.song_mid, args.format): song
                            for song in album.songs}

        cover_resp = session_request(album.album_cover_bg_url)
        album.album_cover_content = cover_resp.content if cover_resp.status_code == 200 else b''

        download_futures = {}
        for future in as_completed(song_url_futures):
            try:
                result = future.result()
            except Exception as e:
                song = song_url_futures[future]
                print(f'{e}, {song.singer_name} - {album.album_name} - '
                      f'[{song.song_mid} {args.format}] {song.song_name}')
            else:
                song = song_url_futures[future]
                song.url = result
                song_info = SongInfo(
                    song_mid=song.song_mid,
                    song_name=song.song_name,
                    singers_mid=song.singers_mid,
                    singers_name=song.singers_name,
                    album_mid=album.album_mid,
                    album_name=album.album_name,
                    album_singers_mid=album.singers_mid,
                    album_singers_name=album.singers_name,
                    album_cover_url=album.album_cover_bg_url,
                    album_cover_content=album.album_cover_content,
                    song_index=song.song_index,
                    company=album.company,
                    genre=song.genre,
                    introduction=None,
                    language=album.language,
                    publish_time=album.publish_time,
                    url=result,
                    str_media_mid=song.str_media_mid
                )
                download_futures[pool.submit(download_with_tags, args.filename(song_info),
                                             song_info, args.overwrite, args.retag)] = song_info
        wait(download_futures)
    return album


def _download_by_song_mid(song_mid, args):
    song_info = get_song_info(song_mid)
    assert song_info.song_mid, f'Song <{song_mid}> not found!'
    song_info.url = get_song_url(song_info.song_mid, args.format)
    song_info.album_cover_content = session_request(song_info.album_cover_bg_url).content
    download_with_tags(args.filename(song_info), song_info, args.overwrite, args.retag)


def download(args: DownloadArgs):
    if not any([args.singer, args.album, args.keywords]):
        return _download_by_song_mid(args.resource, args)

    if args.singer:
        albums = get_singer_albums(args.resource, page=args.page, page_size=args.page_size)
        assert albums, f'Singer <{args.resource}> not found!'
        singer = Singer(singer_mid=args.resource, singer_name=albums[0].singer_name, albums=albums)
    elif args.album:
        album = get_album(args.resource)
        assert album.album_mid, f'Album <{args.resource}> not found!'
        singer = Singer(singer_mid=album.singer_mid, singer_name=album.singer_name, albums=[album])
    else:
        result = search(args.resource, page=1, page_size=1)
        assert result, f'Resource <{args.resource}> not found!'
        return _download_by_song_mid(result[0].song_mid, args)

    for album in args.filter_albums(singer.albums):
        fetch_album_chore(album, args)
