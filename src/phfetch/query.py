'''
Query module for PHFetch.
'''

from phfetch import utils
from phfetch.core import Video, requests

PAGELEN = 32

class Query:
    
    def __init__(self, query: str, session: str = None) -> None:
        '''
        Make a search query on Pornhub.
        
        Arguments
            query: Words to search.
            session: Session to send requests to.
        
        Can be used as generator or as item container.
        Note - This object does not cache requests so for optimisation
               please do not ask the same video twice, save it instead.
        '''
        
        # Intialise session
        self.session = session or requests.Session()
        self.session.cookies.set('accessAgeDisclaimerPH', '1')
        self.url = utils.root + f'video/search?search={query}'
        
        # Current indexes
        self.index: int = 0
        self.length: int = None
        
        self.page: str = None
        self.videos: list[tuple[str]] = None

    def __getitem__(self, index: int) -> Video:
        '''
        Get a single video at a certain index.
        '''
        
        # Handle relative indexes
        if index < 0: index += len(self)
        
        page_index = index // PAGELEN
        
        if self.page is None or self.index != page_index:
            # Update the page
            
            self.get_page(page_index)
            self.index = page_index
        
        # Get the needed video
        key, title = self.videos[ index % PAGELEN ]
        
        obj = Video(key = key, preload = False)
        obj.data = {'video_title': title} # Inject title for opti
        return obj
    
    def __len__(self) -> int:
        '''
        Get the amount of videos.
        '''
        
        # Load a page if needed
        if self.length is None:
            self.get_page(self.index)
        
        return self.length
    
    def get_page(self, index: int) -> None:
        '''
        Fetch a specific query page by index.
        (0-based index)
        '''
        
        # Fetch page
        res = self.session.get(f'{self.url}&page={index + 1}')
        assert res.ok, ConnectionError
        raw = res.text
        
        # Define query length if not defined yet
        if self.length is None:
            counter = utils.re_query_counter.findall(raw)
            assert len(counter), 'Failed to get page counter'
            self.length = int(counter[0])
         
        # Parse videos and save
        self.videos = utils.re_query_videos.findall(raw)
        self.page = raw


# Set up aliases
query = search = Query

# EOF