# @Author: allen
# @Date: May 05 15:56 2020
import os
from typing import List

from dateutil import parser
from pydantic import BaseModel

from musicftdl.utils import convert_to_safe_filename, mkdirs_if_not_exist


class API(BaseModel):
    search: str = 'https://api.qq.jsososo.com/search?key={}&pageNo={}&pageSize={}'
    singer_album: str = 'https://api.qq.jsososo.com/singer/album?singermid={}&pageNo={}&pageSize={}'
    album: str = 'https://api.qq.jsososo.com/album?albummid={}'
    album_songs: str = 'https://api.qq.jsososo.com/album/songs?albummid={}'
    song_info: str = 'https://api.qq.jsososo.com/song?songmid={}'
    song_url: str = 'https://api.qq.jsososo.com/song/url?id={}&type={}'


class Consts(BaseModel):
    api: API = API()
    headers: dict = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                                   'like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    proxies: dict = {'http': 'http://10.57.197.116:50030', 'https': 'https://10.57.197.116:50030'}
    timeout: tuple = (15, 30)


class SearchResult(BaseModel):
    singers_mid: list= None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    song_mid: str = None
    song_name: str = None
    str_media_mid: str = None

    @property
    def singer_mid(self):
        if self.singers_mid:
            return self.singers_mid[0]

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)


class Song(BaseModel):
    singers_mid: list= None
    singers_name: list = None
    song_mid: str = None
    song_name: str = None
    song_index: int = None
    url: str = None
    str_media_mid: str = None

    @property
    def singer_mid(self):
        if self.singers_mid:
            return self.singers_mid[0]

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)


class Album(BaseModel):
    singers_mid: list = None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    album_type: str = None
    album_index: int = None
    company: str = None
    publish_time: str = None
    album_cover_url: str = None
    album_cover_content: bytes = None
    songs: List[Song] = None

    @property
    def singer_mid(self):
        if self.singers_mid:
            return self.singers_mid[0]

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)

    @property
    def publish_date(self):
        return parser.parse(self.publish_time)


class Singer(BaseModel):
    singer_mid: str = None
    singer_name: str = None
    albums: List[Album] = None


class SongInfo(BaseModel):
    song_mid: str = None
    song_name: str = None
    singers_mid: list= None
    singers_name: list = None
    album_mid: str = None
    album_name: str = None
    album_cover_url: str = None
    album_cover_content: bytes = None
    song_index: int = None
    company: str = None
    genre: str = None
    introduction: str = None
    language: str = None
    publish_time: str = None
    url: str = None
    str_media_mid: str = None

    @property
    def lead_singer_mid(self):
        if self.singers_mid:
            return self.singers_mid[0]

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)

    @property
    def lead_singer_name(self):
        if self.singers_name:
            return self.singers_name[0]

    @property
    def publish_date(self):
        return parser.parse(self.publish_time)


class DownloadArgs(BaseModel):
    resource: str = None
    singer: bool = False
    album: bool = False
    fuzzy: bool = False
    overwrite: bool = False
    destination: str = None
    name_style: int = None
    classified: bool = True
    format: str = None
    page: int = None
    page_size: int = None

    @property
    def extension(self):
        if self.format in ['128', '320']:
            return '.mp3'
        else:
            return '.' + self.format

    def format_name(self, song: SongInfo):
        if self.name_style == 3:
            basename = f'{song.singer_name} - {song.album_name} - {song.song_name}{self.extension}'
        elif self.name_style == 2:
            basename = f'{song.singer_name} - {song.song_name}{self.extension}'
        else:
            basename = f'{song.song_name}{self.extension}'
        return convert_to_safe_filename(basename)

    def filename(self, song: SongInfo):
        basename = self.format_name(song)
        paths = [self.destination,
                 convert_to_safe_filename(song.lead_singer_name),
                 convert_to_safe_filename(song.album_name)]
        if self.classified:
            folder = os.path.join(*paths)
        else:
            folder = paths[0]
        mkdirs_if_not_exist(folder)
        return os.path.join(folder, basename)
