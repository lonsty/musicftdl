# @Author: allen
# @Date: May 05 15:56 2020
from typing import List

from dateutil import parser
from pydantic import BaseModel


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
    def singer_name(self):
        return '&'.join(self.singers_name)


class Song(BaseModel):
    song_mid: str = None
    song_name: str = None
    song_index: int = None
    singers_mid: list= None
    singers_name: list = None
    url: str = None
    str_media_mid: str = None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)


class Album(BaseModel):
    album_mid: str = None
    album_name: str = None
    album_type: str = None
    Album_index: int = None
    company: str = None
    publish_time: str = None
    singers_mid: list = None
    singers_name: list = None
    album_cover_url: str = None
    album_cover_content: bytes = None
    songs: List[Song] = None

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
    song_index: int = None
    company: str = None
    genre: str = None
    introduction: str = None
    language: str = None
    publish_time: str = None
    # url: str = None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)

    @property
    def publish_date(self):
        return parser.parse(self.publish_time)


class DownloadArgs(BaseModel):
    resource: str = None
    singer: bool = None
    album: bool = None
    fuzzy: bool = None
    destination: str = None
    name_style: int = None
    classified: bool = None
    format: str = None

    @property
    def extension(self):
        if self.format in ['128', '320']:
            return '.mp3'
        else:
            return '.' + self.format

    def format_name(self, song: SongInfo):
        if self.name_style == 3:
            return f'{song.singer_name} - {song.album_name} - {song.song_name}{self.extension}'
        elif self.name_style == 2:
            return f'{song.singer_name} - {song.song_name}{self.extension}'
        else:
            return f'{song.song_name}{self.extension}'
