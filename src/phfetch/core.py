import os
import requests
from typing import Callable

from phfetch import utils


class Video:
    def __init__(self,
                 url: str = None,
                 key: str = None,
                 session: requests.Session = None,
                 preload: bool = True) -> None:
        '''
        Represents a Pornhub video.
        '''
        
        if url:
            assert 'viewkey=' in url
            self.url = url
            self.viewkey = url.split('viewkey=')[1]
        
        else:
            assert key
            self.url = utils.base + key
            self.viewkey = key
        
        self.data: dict = None
        self.session = session or requests.Session()
        
        if preload:
            self._fetch()
    
    def __str__(self) -> str:
        return f'<Video url={self.viewkey}>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def _lazy_fetch(self) -> dict:
        '''
        Fetch the data if needed.
        '''
        
        if not self.data: self._fetch()
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
        
        return self._lazy_fetch().get('video_title', 1)
    
    @property
    def hotspots(self) -> list[int]:
        '''
        A list of the hotspots of the video.
        '''
        
        li = self._lazy_fetch().get('hotspots')
        return list(map(int, li))
    
    def _fetch(self) -> None:
        '''
        Fetch the HTML page and what's intersting in it.
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
    
    def _get_segments(self, quality: str = 'best') -> list[str]:
        '''
        Fetch the video fragments.
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
        
        raw = self.session.get(segment_base + segments_url)
        assert raw.ok, 'Connection error'
        
        # Parse file and append base URL
        return [segment_base + url
                for url in utils.parse_M3U(raw.text)]
    
    def download(self,
                 path: str,
                 quality: str = 'best',
                 verbose: bool = True,
                 thread: bool = False,
                 callback: Callable = print) -> str:
        '''
        Download the video at a certain path.
        If the specified path is a directory,
        add the video to the dir with a custom*
        name.
        Returns the path it was written to.
        
        TODO - multithread downloading
        '''
        
        segments = self._get_segments(quality)
        
        if verbose: callback('[*] Fetched M3U data')
        
        if os.path.isdir(path):
            name = utils.nameify(self.title)
            path = path + f'{name}.mp4'
        
        print('saving as', name)
        
        if verbose: callback('[*] Using path', path)
        
        with open(path, 'wb') as output:
            
            for i, url in enumerate(segments):

                raw = self.session.get(url)
                
                # print(raw.content)
                
                output.write(raw.content)
            
                if verbose:
                    
                    if callback is print:
                        callback(f'[*] Downloading \033[91m{self.viewkey}\033[0m: \033[92m{i}\033[0m/{len(segments)}')
                    else:
                        callback('Downloading', i, len(segments))
        
        callback('[*] Operation done successfully.')
        return path

# EOF