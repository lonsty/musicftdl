# @Author: allen
# @Date: May 05 15:56 2020
import os
from typing import List

from dateutil import parser
from pydantic import BaseModel, validator

from musicftdl.utils import (convert_seconds_to_dtstr,
                             convert_to_safe_filename, mkdirs_if_not_exist)


class API(BaseModel):
    search: str = 'http://mapi.lonsty.me/search?key={}&pageNo={}&pageSize={}'
    singer_album: str = 'http://mapi.lonsty.me/singer/album?singermid={}&pageNo={}&pageSize={}'
    album: str = 'http://mapi.lonsty.me/album?albummid={}'
    album_songs: str = 'http://mapi.lonsty.me/album/songs?albummid={}'
    song_info: str = 'http://mapi.lonsty.me/song?songmid={}'
    song_url: str = 'http://mapi.lonsty.me/song/url?id={}&type={}'


class Consts(BaseModel):
    api: API = API()
    headers: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                   '(KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'}
    proxies = {
        'http': 'http://183.129.244.16:33238',
        'https': 'https://183.129.244.16:33238'
    }
    timeout: tuple = (15, 30)


class SearchResult(BaseModel):
    singers_mid: list= None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    song_mid: str = None
    song_name: str = None
    duration: int = None
    str_media_mid: str = None

    @validator('duration')
    def convert_int_to_str(cls, v):
        return convert_seconds_to_dtstr(v)

    @property
    def singer_mid(self):
        return self.singers_mid[0] if self.singers_mid else None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name) if self.singers_name else None


class Song(BaseModel):
    singers_mid: list= None
    singers_name: list = None
    song_mid: str = None
    song_name: str = None
    song_index: int = None
    duration: int = None
    genre: int = None
    url: str = None
    str_media_mid: str = None

    @validator('duration')
    def convert_int_to_str(cls, v):
        return convert_seconds_to_dtstr(v)

    @property
    def singer_mid(self):
        return self.singers_mid[0] if self.singers_mid else None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name) if self.singers_name else None


class Album(BaseModel):
    singers_mid: list = None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    album_type: str = None
    album_index: int = None
    language: str = None
    song_count: int = None
    company: str = None
    publish_time: str = None
    album_cover_url: str = None
    album_cover_content: bytes = None
    songs: List[Song] = None

    @property
    def singer_mid(self):
        return self.singers_mid[0] if self.singers_mid else None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name) if self.singers_name else None

    @property
    def publish_date(self):
        return parser.parse(self.publish_time)

    @property
    def album_cover_bg_url(self):
        if self.album_mid:
            return f'https://y.gtimg.cn/music/photo_new/T002R800x800M000{self.album_mid}.jpg?max_age=2592000'

    @property
    def singer_pic_bg_url(self):
        if self.singer_mid:
            return f'https://y.gtimg.cn/music/photo_new/T001R800x800M000{self.singer_mid}.jpg?max_age=2592000'


class Singer(BaseModel):
    singer_mid: str = None
    singer_name: str = None
    albums: List[Album] = None


class SongInfo(BaseModel):
    song_mid: str = None
    song_name: str = None
    duration: int = None
    singers_mid: list= None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    album_singers_mid: list = None
    album_singers_name: list = None
    song_index: int = None
    company: str = None
    introduction: str = None
    language: str = None
    genre: int = None
    publish_time: str = None
    url: str = None
    album_cover_url: str = None
    album_cover_content: bytes = None
    str_media_mid: str = None

    @validator('duration')
    def convert_int_to_str(cls, v):
        return convert_seconds_to_dtstr(v)


    @property
    def singer_name(self):
        return '&'.join(self.singers_name) if self.singers_name else None

    @property
    def album_singer_name(self):
        return '&'.join(self.album_singers_name) if self.album_singers_name else self.singer_name

    @property
    def publish_date(self):
        return parser.parse(self.publish_time)

    @property
    def album_cover_bg_url(self):
        if self.album_mid:
            return f'https://y.gtimg.cn/music/photo_new/T002R800x800M000{self.album_mid}.jpg?max_age=2592000'


class DownloadArgs(BaseModel):
    resource: str = None
    singer: bool = False
    album: bool = False
    keywords: bool = False
    overwrite: bool = False
    destination: str = None
    name_style: int = None
    album_types: str = 'SELO'
    classified: bool = True
    format: str = None
    page: int = None
    page_size: int = None
    proxy: str = None

    @property
    def extension(self):
        return 'mp3' if self.format in ['128', '320'] else self.format

    def format_name(self, song: SongInfo) -> str:
        if self.name_style == 3:
            basename = f'{song.singer_name} - {song.album_name} - {song.song_name}.{self.extension}'
        elif self.name_style == 2:
            basename = f'{song.singer_name} - {song.song_name}.{self.extension}'
        else:
            basename = f'{song.song_name}.{self.extension}'
        return convert_to_safe_filename(basename)

    def filename(self, song: SongInfo) -> str:
        basename = self.format_name(song)
        paths = [self.destination,
                 convert_to_safe_filename(song.album_singer_name),
                 convert_to_safe_filename(song.album_name)]
        folder = os.path.join(*paths) if self.classified else paths[0]
        mkdirs_if_not_exist(folder)
        return os.path.join(folder, basename)

    def filter_albums(self, albums: List[Album]) -> List[Album]:
        types_mp = {'S': '录音室专辑', 'E': 'EP单曲', 'L': '现场专辑', 'O': '其他'}
        types = [types_mp.get(k) for k in list(self.album_types.upper())]
        return [album for album in albums if album.album_type in types or '其他' in types]

    @property
    def retag(self):
        return True if self.format in ['128', '320'] else False

    @property
    def proxies(self):
        proxies = None
        if self.proxy:
            proxies = {
                'http': f'http://{self.proxy}',
                'https': f'https://{self.proxy}'
            }
        return proxies
