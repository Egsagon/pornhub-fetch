# DEPRECATED - USE [PHUB](https://github.com/Egsagon/PHUB) INSTEAD

--------------------------------

# PH Fetch

A light python interface for fetching and downloading videos from PornHub.

LICENSE: MIT - See the `LICENSE` file.

## Installation
Install using pip on python 3.11 or higher:
```
pip install phfetch
```
Or clone this repository to get the latest release.

## Usage
Sample script to download a video given its URL:
```py
import phfetch

video = phfetch.video(url = 'https://...')
# Or using directly the video viewkey
video = phfetch.video(key = '..........')

video.download('video.mp4', quality = 'best')
```

Sample script to search videoe:
```py
result = phfecth.search('...')

# Get a specific video
print(result[0])

# Get the amount of available videos
# Note: in some cases, the number provided by PornHub
# is wrong. Going further this number will raise errors.
print(len(result))

# Endless scroll through videos:
for video in result:
  print(video.title)
```

## PornHub API wrapper
Alongside being able to download videos, this API is able to parse some useful PornHub video informations, stored in all `phfetch.Video` objects.
| property            | Type        | Description                                       |
| ------------------- | ----------- | ------------------------------------------------- |
| `video.title`       | `str`       | Title of the video                                |
| `video.image`       | `str`       | URL of the thumbnail                              |
| `video.duration`    | `int`       | Video duration in seconds                         |
| `video.hotspots`    | `list[int]` | List of hotspots location in seconds              |
| `video.orientation` | `bool`      | Whether the video is in landscape mode            |
| `video.views`       | `Vote`      | Object with `up` and `down` attributes            |
| `video.tags`        | `list[Tag]` | List of objectd with `name` and `count` attibutes |
| `video.datalayer`   | `dict`      | Advanced data provided by PornHub (can be useful) |
| `video.author`      | `Author`    | Object representing a PornHub user                |

Note: All these properties are cached. If you want to reload them, use `video.refresh()`.

`Author` object have the following attributes:
| attribute     | Type          | Description                      |
| ------------- | ------------- | -------------------------------- |
| `url`         | `str`         | URL that leads to author profile |
| `name`        | `str`         | Author profile name              |
| `model_type`  | `str`         | The author model type            |
| `videos`      | `list[Video]` | Author videos (not implemented)  |
| `subscribers` | `int`         | Amount of people subscribed (not implemented) |

Note: `Author` objects are comparable.

## Advanced downloading
To extract a video without dowloading it, call one of these functions:
```py
video.M3U(quality = 'best') # Get the raw M3U8 file of the video
```
```py
video.get_segments(quality = 'best') # Same as before but parses the file to get only URLs
```

This can be useful if you want to use a threaded download script of FFMPEG to download the video faster (currently, PHFetch just fetches one segment at a time and append it to a file).

## Why?
This is a way of replacing `yt-dl` which is not able anymore (as of today) to download videos from PornHub. I understand this is messy (especially the author and searching stuff) and am planning to make a bigger API with better client-like structure.
