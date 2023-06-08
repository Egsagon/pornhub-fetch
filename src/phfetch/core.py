from __future__ import annotations

import os
import json
import requests
from dataclasses import dataclass
from typing import Callable, Self

from phfetch import utils


@dataclass
class Vote:
    up: str
    down: str

@dataclass
class Tag:
    name: str
    count: int
    
    def __post_init__(self) -> None:
        self.count = int(self.count)

@dataclass
class Author:
    url: str
    name: str
    model_type: str
    videos: str
    subscribers: str
    
    @classmethod
    def parse(cls, video: Video) -> Self:
        '''
        Parse the author from a video page.
        '''
        
        return cls(
            
            # TODO
            url = None,
            videos = None,
            subscribers = None,
            
            name = video.datalayer['videodata']['video_uploader_name'],
            model_type = video.datalayer['videodata']['video_uploader']
            
        )
    
    def __eq__(self, other: Author) -> bool:
        '''
        Compares two authors.
        '''
        
        return self.url == other.url


class Video:
    def __init__(self,
                 url: str = None,
                 key: str = None,
                 session: requests.Session = None,
                 preload: bool = True,
                 search_data: dict = None) -> None:
        '''
        Represents a Pornhub video.
        
        Arguments
            url: video url.
            key: video viewkey (in replacment for url).
            session: optional session to inherit from.
            preload: wether to fetch on initialisation.
            search_data: data passed by the search module.
        '''
        
        if url:
            assert 'viewkey=' in url
            self.url = url
            self.viewkey = url.split('viewkey=')[1]
        
        else:
            assert key
            self.url = utils.base + key
            self.viewkey = key
        
        self.page: str = None
        self.data: dict = None
        self._datalayer: dict = None
        self.session = session or requests.Session()
        
        self.search_data = search_data
        
        if preload:
            self.refresh()
    
    def __str__(self) -> str:
        return f'<phfetch.Video key={self.viewkey}>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def _lazy_fetch(self) -> dict:
        '''
        Same as refresh but using a cache system.
        '''
        
        if not self.data: self.refresh()
        return self.data
    
    @property
    def available(self) -> bool:
        '''
        Whether a video is available.
        '''
        
        return self._lazy_fetch().get('video_unavailable', 1)
    
    @property
    def duration(self) -> int:
        '''
        The video duration, in whatever unit Pornhub uses.
        '''
        
        return self._lazy_fetch().get('video_duration')
    
    @property
    def tags(self) -> list[Tag]:
        '''
        The referenced video tags.
        '''
        
        tags = self._lazy_fetch().get('actionTags').split(',')
        return [Tag(*tag.split(':')) for tag in tags]
    
    @property
    def votes(self) -> Vote:
        '''
        Up and down thumbs.
        '''
        
        matches = utils.re_votes.findall(self.page)
        votes = {t.lower(): v for t, v in matches}
        
        return Vote(self, votes['up'], votes['down'])
    
    @property
    def views(self) -> int:
        '''
        The amount of people that watched that video.
        '''
        
        self._lazy_fetch()
        raw = utils.re_interdata.findall(self.page)[0]
        data = json.loads(f'[{raw}]')
        
        return int(data[0]['userInteractionCount'].replace(' ', ''))
    
    @property
    def datalayer(self) -> dict:
        '''
        Parsed data layer provided by Pornhub for advanced infos.
        '''
        
        self._lazy_fetch()
        
        if self._datalayer is None:
            
            raw = utils.re_datalayer.findall(self.page)[0]
            self._datalayer = json.loads(raw.replace("'", '"'))
        
        return self._datalayer
    
    @property
    def author(self) -> Author:
        '''
        The author account of the video.
        '''
        
        self._lazy_fetch()
        return Author.parse(self)
    
    @property
    def orientation(self) -> bool:
        '''
        True -> Landscape mode
        False -> Portrait mode
        '''
        
        return not bool(self._lazy_fetch().get('isVertical'))
    
    @property
    def image(self) -> str:
        '''
        Get the video thumbnail url.
        '''
        
        return self._lazy_fetch().get('image_url')
    
    @property
    def title(self) -> str:
        '''
        The video title.
        '''
        
        return self._lazy_fetch().get('video_title')
    
    @property
    def hotspots(self) -> list[int]:
        '''
        A list of the hotspots of the video.
        '''
        
        li = self._lazy_fetch().get('hotspots')
        return list(map(int, li))
    
    def refresh(self) -> None:
        '''
        Fetch the video page.
        Can be used to refresh video data.
        '''
        
        # Add cookie to remove age confirmation popup
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        
        # Fetch the given URL
        res = self.session.get(self.url)
        
        # Error protection
        if not res.ok:
            raise ConnectionError('Failed to connect to Pornhub:', res.status_code)
        
        # Fetch infos
        self.data = utils.resolve_script(res.text)
        self.page = res.text
    
    def M3U(self, quality: str = 'best') -> str:
        '''
        Get the url of the M3U file representing
        a certain video quality.
        
        Arguments
            quality: needed quality of the video.
        
        Returns
            an URL.
        '''
        
        # Get master URL for the quality
        qualities = self._lazy_fetch()['mediaDefinitions']
        url = utils.get_quality_url(qualities, quality)
        
        # Fetch the master M3U file
        raw = self.session.get(url)
        assert raw.ok, 'Connection error'
        
        # Fetch the M3U segments file
        segment_base = url.split('master.m3u8')[0]
        segments_url = utils.parse_M3U(raw.text)[0]
        
        return segment_base + segments_url
    
    def get_segments(self, quality: str = 'best') -> list[str]:
        '''
        Fetch and parse the video segments.
        
        Arguments
            quality: needed quality of the video.
        
        Returns
            A list of complete urls for each video segment.
        '''
        
        # Get M3U url
        url = self.M3U(quality)
        base = os.path.dirname(url) + '/'
        
        raw = self.session.get(url)
        assert raw.ok, 'Connection failure'
        
        # Parse file and append base URL
        return [base + url
                for url in utils.parse_M3U(raw.text)]
    
    def download(self,
                 path: str,
                 quality: str = 'best',
                 quiet: bool = False,
                 callback: Callable[[int, int], None] = None) -> str:
        '''
        Locally download the video.
        
        Arguments
            path:     filepath/dirpath to the download location.
            quality:  needed quality of the video.
            quiet:    wether to print current download status.
            callback: optionnal function to call on download update.
        
        Note - The callback will receive the current index and the total
        as arguments.
        
        Returns
            The path it has written the file to.
        '''
        
        segments = self.get_segments(quality)
        
        if not quiet:
            print('[*] Fetched M3U data')
        
        if os.path.isdir(path):
            # NOTE - We could choose to set the default name as the video
            # title or its viewkey. I prefer the viewekey because cleaner
            
            # path = path + f'{utils.nameify(self.title)}.mp4'
            path = path + f'{self.viewkey}.mp4'
        
        with open(path, 'wb') as output:
            for i, url in enumerate(segments):

                raw = self.session.get(url)
                assert raw.ok, 'Connection failure'
                output.write(raw.content)
            
                if not quiet:
                    print(f'\r[*] Downloading \033[92m{i}\033[0m/{len(segments)}', end = '')
                
                # Send to callback if exists
                if callable(callback):
                    callback(i, len(segments))
        
        if not quiet:
            print(f'\n[*] Downloaded \033[93m{self.viewkey}\033[0m.')
        
        return path

# EOF