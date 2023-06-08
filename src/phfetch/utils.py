import re
import json
import string

root = 'https://fr.pornhub.com/'
base = root + 'view_video.php?viewkey='

# Video pages regexes
re_comments = re.compile(r'\/\*.*?\*\/')
re_flash = re.compile(r'var (flashvars_\d*) = ({.*});\n')
re_votes = re.compile(r'span class=\"votes(Up|Down)\" data-rating.*?>(.*?)<')

# JS regexes
re_datalayer = re.compile(r'window\.dataLayer\.push\(({.*?})\);', re.DOTALL)
re_interdata = re.compile(r'interactionStatistic\": \[(.*?)\]', re.DOTALL)

# Query regexes
re_query_counter = re.compile(r'showingCounter\">.*? (\d+) +</', re.DOTALL)
re_query_videos = re.compile(r'<li .*?videoblock.*?data-video-vkey=\"(.*?)\".*?title=\"(.*?)\"', re.DOTALL)


class Quality:
    BEST = 'best'
    MIDDLE = 'middle'
    WORST = 'worst'

def resolve_script(raw: str) -> dict:
    '''
    Resolve Pornhub obfuscation on the M3U master file.
    The obfuscation itself is just a js script glueing
    back together parts ot the URL in a random order.
    
    We could use some regex magic but i prefer translating
    this to a python script and then executing it, way easier.
    
    Arguments
        raw: raw content of the HTML page.
        
    Returns
        a dictionnary containing some video data and the clear
        video data.
    '''
    
    flash, ctx = re_flash.findall(raw)[0]
    script = raw.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    
    # Load context
    data: dict = json.loads(ctx)
    
    # Format the script
    script = ''.join(script.replace('var', '').split())
    script = re_comments.sub('', script)
    script = script.replace(flash.replace('var', ''), 'data')
    
    # Execute the script
    exec(script)
    
    return data

def get_closest_value(iter: list[int], value: int):
    '''
    Pick the closest value in a list.
    From www.entechin.com/find-nearest-value-list-python/
    '''
    
    difference = lambda input_list: abs(input_list - value)
    return min(iter, key = difference)

def get_quality_url(data: dict,
                    quality: str | int,
                    warn: bool = True) -> str:
    '''
    Find the best fitting quality among a list of M3U URLs.
    
    Arguments
        data: dictionnary containing the available qualities.
        quality: desired video quality.
        warn: wether to warn when desired quality is not available.

    Returns
        The URL of the M3U file for that quality.
    '''
    
    qualities = {
        int(el['quality']): el['videoUrl'] for el in data
        if el['quality'] in ['1080', '720', '480', '240']
    }
    
    # If key is an absolute value
    if isinstance(quality, int):
        key = quality
        
        # Try to find nearest if does not exists
        if not key in qualities:
            
            if warn:
                print(f'\033[93mWarn: Quality {key} not found, picking nearest one.\033[0m')
            
            key = get_closest_value(qualities.keys(), key)
    
    # If key is a string or a 'Quality' constant
    elif isinstance(quality, str):
        
        match quality.lower():
            case 'best': key = max(qualities.keys())
            case 'worst': key = min(qualities.keys())
            case 'middle':
                keys = sorted(qualities.keys())
                key = keys[len(keys) // 2]
            
            case ukn:
                raise TypeError('Invalid quality type', ukn)
    
    else:
        raise TypeError('Invalid quality type', ukn)
    
    return qualities[key]

def parse_M3U(raw: str) -> list[str]:
    '''
    Convert a raw M3U file to a list of URLs.
    '''
    
    return [l for l in raw.split('\n')
            if l and not l.startswith('#')]

def nameify(title: str) -> str:
    '''
    Transform a title to a path safe name.
    '''
    
    allowed = string.ascii_letters + string.digits + ' '
    
    return '-'.join(''.join(char for char in title
                            if char in allowed).strip().split()).lower()

# EOF