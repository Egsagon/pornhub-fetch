from playwright.sync_api import sync_playwright as plw


def conclude(req) -> bool:
    '''
    Predicate if a request is a valid M3U.
    '''
    
    print(req)
    
    return False


def fetch(url: str) -> str:
    '''
    Fetch raw M3U file.
    '''
    
    with plw() as core:
        
        browser = core.firefox.launch(headless = False)
        
        page = browser.new_page()
        page.goto(url)
        
        with page.expect_request_finished(conclude) as conc:
            
            data = [conc]
        
        browser.close()
    
    return data


if __name__ == '__main__':
    fetch(open('src.txt').read())

# EOF