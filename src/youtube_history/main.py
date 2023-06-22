from ak_selenium import Chrome, By
import time
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement
from dataclasses import dataclass

@dataclass
class Keywords:
    path: Path
    items: list[str] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = get_keywords(self.path)
    
@dataclass
class VideoInfo:
    element: WebElement
    title: str = None
    channel: str = None
    description: str = None
    
    def __post_init__(self):
        self.title = self.element.find_element(By.ID, 'title-wrapper').text.strip()
        self.channel= self.element.find_element(By.ID, 'metadata').find_element(By.ID, 'channel-name').text.strip()
        self.description = self.element.find_element(By.ID, 'description-text').text.strip()
        
    @property
    def text(self) -> str:
        return f"{self.title} {self.channel} {self.description}".lower()
    
    def to_remove(self, 
                  channelblack: Keywords,
                  keywordblack: Keywords,
                  channelwhite: Keywords,
                  keywordwhite: Keywords) -> bool:
        if self.channel.casefold() in channelwhite.items or any(keyword in self.text for keyword in keywordwhite.items):
            return False
        elif self.channel.casefold() in channelblack.items or any(keyword in self.text for keyword in keywordblack.items):
            return True
        else:
            return False

class Scrubber:
    def __init__(
        self, 
        keywords_blacklist: str = Path('keyword-blacklist.txt'), 
        keywords_whitelist: str = Path('keyword-whitelist.txt'), 
        channel_blacklist: str = Path('channel-blacklist.txt'), 
        channel_whitelist: str = Path('channel-whitelist.txt')):
        
        self.chrome = Chrome(headless=False,half_screen=True)
        self.driver = self.chrome.init_chrome()
        self.driver.get('https://www.youtube.com/feed/history')
        self.check_login()
        
        self.keywords_blacklist = Keywords(path=keywords_blacklist)
        self.keywords_whitelist = Keywords(path=keywords_whitelist)
        self.channel_blacklist = Keywords(path=channel_blacklist)
        self.channel_whitelist = Keywords(path=channel_whitelist)
        
    def __repr__(self) -> str:
        return f"Scrubber({self.keywords_blacklist.path.name=}\n \
            {self.keywords_whitelist.path.name=}\n \
            {self.channel_blacklist.path.name=}\n \
            {self.channel_whitelist.path.name=})"
        
    def check_login(self):
        """Check if Account is logged in
        """
        chrome = self.chrome
        driver = self.driver

        if chrome.find_element_by_text(
            elements=driver.find_elements(By.TAG_NAME, 'span'),
            text='Sign in'):
            import sys
            del chrome
            Exception('Google Account is not logged in. \n\
                Open Chrome and log into your google account')
            sys.exit()


    
    def scrub_videos(self) -> None:            
        driver = self.driver
        
        # Get Video Containers
        video_containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        for video_container in video_containers:
            video_info = VideoInfo(video_container)
            print(f"{video_info.title} by {video_info.channel}...", end='')
            # Look for keywords in container text
            if video_info.to_remove(
                channelblack=self.channel_blacklist,
                keywordblack=self.keywords_blacklist,
                channelwhite=self.channel_whitelist,
                keywordwhite=self.keywords_whitelist):
                
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
        
    def write_scrublist(self) -> None:
        for each in (self.channel_blacklist, self.channel_whitelist, 
                     self.keywords_blacklist, self.keywords_whitelist):
            
            # Remove duplicates using set()
            keywords = list(set(each.items))

            # Sort the list alphabetically using sorted()
            keywords = sorted(keywords)

            with open(each.path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(keywords))

        
def get_keywords(filepath: Path) -> list[str]:
    if not filepath.exists():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write()
        keywords = []
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            keywords = f.readlines()
        keywords = [item.lower().strip() for item in keywords if item.strip()]
    return keywords