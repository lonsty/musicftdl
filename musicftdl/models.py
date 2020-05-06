# @Author: allen
# @Date: May 05 15:56 2020
from typing import List

from pydantic import BaseModel


class API(BaseModel):
    search: str = 'https://api.qq.jsososo.com/search?key={}&pageSize={}'
    singer_album: str = 'https://api.qq.jsososo.com/singer/album?singermid={}&pageSize={}'
    album: str = 'https://api.qq.jsososo.com/album?albummid={}'
    album_songs: str = 'https://api.qq.jsososo.com/album/songs?albummid={}'
    song_url: str = 'https://api.qq.jsososo.com/song/url?id={}&type={}'


class Consts(BaseModel):
    api: API = API()
    headers: dict = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                                   'like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    proxies: dict = {'http': 'http://10.57.197.116:50030', 'https': 'https://10.57.197.116:50030'}
    timeout: tuple = (5, 10)


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
    songs: List[Song] = None

    @property
    def singer_name(self):
        return '&'.join(self.singers_name)


class Singer(BaseModel):
    singer_mid: str = None
    singer_name: str = None
    albums: List[Album] = None
