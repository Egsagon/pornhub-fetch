'''
pornhub_fetch - Pornhub video downloading interface

See https://github.com/Egsagon/pornhub-fetch for docs
'''

from phfetch import core                        # Core (for dataclasses)
from phfetch.utils import Quality               # Quality constants (se)
from phfetch.core import Video, Video as video  # Video object shortcuts
from phfetch.query import Query, query, search  # Query object shortcuts

# EOF