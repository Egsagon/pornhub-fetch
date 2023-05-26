import re
import json
import string

base = 'https://fr.pornhub.com/view_video.php?viewkey='

re_comments = re.compile(r'\/\*.*?\*\/')
re_flash = re.compile(r'var (flashvars_\d*) = ({.*});\n')
re_votes = re.compile(r'span class=\"votes(Up|Down)\" data-rating.*?>(.*?)<')
# re_author = re.compile(r'a href=\"(/channels/.*?)\" data-event.*?>(.*?)<.*?span>(.*?) Videos<.*?<span>(.*?) Subscribers<')

re_author = re.compile(r'a href=\"(\/channels\/.*?)\" data-event.*?>(.*?)<')
re_author_videos = re.compile(r'n>(.*?) Videos', re.M)
re_author_subs = re.compile(r'n>(.*?) Subscribers')

class Quality:
    BEST = 'best'
    MIDDLE = 'middle'
    WORST = 'worst'

def resolve_script(raw: str) -> dict:
    '''
    Get the flash script of an HTML page.
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

def get_quality_url(data: dict, quality: str | int) -> str:
    '''
    Find the best fitting quality among a list of URLs. 
    '''
    
    qualities = {
        int(el['quality']): el['videoUrl'] for el in data
        if el['quality'] in ['1080', '720', '480', '240']
    }
    
    # If key is an absolute value
    if isinstance(quality, int):
        key = quality
    
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
    
    return ''.join(char for char in title if char in allowed)

# EOF