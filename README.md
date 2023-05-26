# PH Fetch

A light python interface for fetching and downloading videos from Pornhub.

## Usage

Initialisation:
```python
import phfetch

# Initialise with a video url
video = phfetch.video( url = 'https://...' )

# Or a viewkey token
video = phfetch.video( key = 'xxxxxxxxxx' )
```

Available video infos:
```python
>>> video.title # The Pornhub title of the video
>>> video.available # Whether the video is available to view (because deleted or not disponible in country)
>>> video.duration # The video duration (in seconds)
>>> video.hotspots # The list of hotspots of the video
```

To download a video:
```python
# Using an absolute or relative file path 
video.download( path = 'my-video.mp4' )

# Using a directory path (the file name will be the video title)
video.download( path = 'my-dir/' )

# Using a specific quality
video.download( path = './', quality = 'best')
# Possible quality values:
# best, middle, worst or an int
# Can also be a constant from pyhub.Quality, e.g:

video.download( path = './', quality = pyhub.Quality.BEST )
```

An example UI implementation can be found in the `ui.py` file:
![image](https://github.com/Egsagon/pornhub-fetch/blob/master/demo.png)

## Installation

Minimum python version: `3.11`
Dependencies: `requests`

Install using pip:
```sh
pip install git+https://github.com/Egsagon/pornhub-fetch.git
```
