import re
import json
import requests

# Compile regexes
re_comments = re.compile(r'\/\*.*?\*\/')
re_flash = re.compile(r'var (flashvars_\d*) = ({.*});\n')


def get_data(url: str) -> dict:
    '''
    Read the target and returns a dict
    containing all video urls.
    '''

    # Initialise the session
    session = requests.Session()

    # Add a cookie to remove the age confirmation popup
    session.cookies.set('accessAgeDisclaimerPH', '1')

    # Fetch the page
    page = session.get(url).text

    # Get media script
    script = page.split("flashvars_['nextVideo'];")[1].split('var nextVideoPlay')[0]
    flash, data = re_flash.findall(page)[0]

    # Create flash
    content: dict = json.loads(data)

    # Remove spaces, comments, js attributions and update the flash variable name
    flash_name = flash.replace('var', '')
    script = re_comments.sub('', ''.join(script.replace('var', '').split())).replace(flash_name, 'content')

    # Execute script
    exec(script)

    return content

def get_M3U8(data: dict, qual: str) -> list[str]:
    '''
    Get the M3U8 file from a data dict.
    '''
    
    # Parse qualities
    quals = {el['quality']: el['videoUrl']
             for el in data['mediaDefinitions'] if el['quality']
             in ['240', '480', '720', '1080']}

    url = quals[qual]
    
    # Fetch the M3U file
    session = requests.Session()
    raw = session.get(url).text
    
    # Parse M3U
    base = url.split('master.m3u8')[0]
    m3u_list = [l for l in raw.split('\n') if not l.startswith('#')][0]
    murl = base + m3u_list
    
    # Get segment list
    segments = [base + l for l in session.get(murl).text.split('\n')
                if l and not l.startswith('#')]
    
    return segments
    
def download(segments: list, path: str) -> None:
    '''
    Download and concat all segments to a file.
    '''
    
    session = requests.Session()
    
    with open(path, 'wb') as file:
        
        for i, segment in enumerate(segments):
            
            raw = session.get(segment).content
            file.write(raw)
            
            print(i, '/', len(segments))
    

if __name__ == '__main__':
    
    # Get data
    url = open('src.txt').read()
    data = get_data(url)
    
    # Get M3U8
    li = get_M3U8(data, '240')
    
    # Download
    download(li, 'test.mp4')

# EOF