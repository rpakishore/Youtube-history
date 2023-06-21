from ak_selenium import Chrome
import time
from pathlib import Path

class Scrubber:
    def __init__(self, keywords_file: Path=None):
        self.chrome = Chrome(
            headless=False,
            half_screen=True
            )
        self.driver = self.chrome.init_chrome()
        self.driver.get('https://www.youtube.com/feed/history')
        self.check_login()
        if not keywords_file:
            keywords_file = Path('scrublist.txt')
        self.keywords_file = keywords_file
        
    def check_login(self):
        """Check if Account is logged in
        """
        chrome = self.chrome
        driver = self.driver
        By, _ = chrome.get_By_and_Keys()

        if chrome.find_element_by_text(
            elements=driver.find_elements(By.TAG_NAME, 'span'),
            text='Sign in'):
            import sys
            del chrome
            Exception('Google Account is not logged in. \n\
                Open Chrome and log into your google account')
            sys.exit()

    def get_keywords(self) -> list[str]:
        if not self.keywords_file.exists():
            with open(self.keywords_file, 'w', encoding='utf-8') as f:
                f.write()
            keywords = []
        else:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                keywords = f.readlines()
            keywords = [item.lower().strip() for item in keywords if item.strip()]
        
        return keywords
    
    def scrub_videos(self, keywords: list[str]=None) -> None:
        if not keywords:
            keywords = self.get_keywords()
            
        chrome = self.chrome
        driver = self.driver
        By, _ = chrome.get_By_and_Keys()
        
        # Get Video Containers
        video_containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        for video_container in video_containers:
            title = video_container.find_element(By.TAG_NAME, 'yt-formatted-string').text
            print(f"{title}...", end='')
            # Look for keywords in container text
            container_text = video_container.text.casefold()
            if any([keyword in container_text for keyword in keywords]):
                # find the dismiss Button
                buttons = video_container.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if button.get_attribute('aria-label') == 'Remove from watch history':
                        button.click()
                        print('Removed')
                        time.sleep(3)
                        break
            else:
                print('Skipped')
                
    def scrub_shorts(self) -> None:
        #Work in Progress
        chrome = self.chrome
        driver = self.driver
        By, _ = chrome.get_By_and_Keys()
        
        reels_containers = driver.find_elements(By.TAG_NAME, 'ytd-reel-shelf-renderer')

        for reels_container in reels_containers:
            try:
                #For each short
                for shorts_container in reels_container.find_elements(By.TAG_NAME, 'ytd-reel-item-renderer'):
                    
                    if shorts_container.text.strip() == 'All views of this video removed from history':
                        continue
                    
                    print(shorts_container.text)
                    # Click `Action menu` button
                    for button in shorts_container.find_elements(By.TAG_NAME, "button"): 
                        if button.get_attribute('aria-label') == 'Action menu':
                            if button.is_enabled():
                                button.click()
                                time.sleep(2)
                            break
                    
                    # Click Remove from watch history
                    elements = driver.find_elements(By.TAG_NAME, "ytd-menu-service-item-renderer")
                    button = chrome.find_element_by_text(elements, 'Remove from watch history')

                    if button:
                        button.click()
                        time.sleep(2)
            except Exception as e:
                print(str(e))
                continue
            
    def __del__(self) -> None:
        del self.chrome
        self.write_scrublist()
        
    def write_scrublist(self, keywords: list[str]=None) -> None:
        if not keywords:
            keywords = self.get_keywords()
        # Remove duplicates using set()
        keywords = list(set(keywords))

        # Sort the list alphabetically using sorted()
        keywords = sorted(keywords)

        with open(self.keywords_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(keywords))
