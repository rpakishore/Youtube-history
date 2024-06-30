from ak_selenium import Chrome, By, Keys
import time
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementNotInteractableException
from dataclasses import dataclass
from typing import Literal
from icecream import ic
ic.disable()

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
    removed_shorts = []
    removed_videos = []

    def __init__(
        self, 
        keywords_blacklist: Path = Path('keyword-blacklist.txt'), 
        keywords_whitelist: Path = Path('keyword-whitelist.txt'), 
        channel_blacklist: Path = Path('channel-blacklist.txt'), 
        channel_whitelist: Path = Path('channel-whitelist.txt')):
        
        self.load_driver()
        self.check_login()
        
        self.keywords_blacklist = Keywords(path=keywords_blacklist)
        self.keywords_whitelist = Keywords(path=keywords_whitelist)
        self.channel_blacklist = Keywords(path=channel_blacklist)
        self.channel_whitelist = Keywords(path=channel_whitelist)
    
        self.write_scrublist()
        
    def load_driver(self) -> None:
        """Load Chromedriver to class attribute
        """
        self.chrome = Chrome()
        self.driver = self.chrome.driver
        self.driver.get('https://www.youtube.com/feed/history')
        
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
        self.load_videos()
        self.__delete_videos()

    def load_videos(self) -> None:
        for _ in range(5):
            _elem = self.driver.find_element(By.TAG_NAME, "html")
            _elem.send_keys(Keys.HOME)
            time.sleep(7)
                
    def __delete_videos(self) -> None:
        print('Removing Videos: ')    
        driver = self.driver
        
        # Get Video Containers
        video_containers = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        for video_container in video_containers:
            video_info = VideoInfo(video_container)
            print(f"\t- {video_info.title} by {video_info.channel}...", end='')
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
                    
                self.removed_videos.append(video_info.title)
            else:
                print('Skipped')
                
    def scrub_shorts(self) -> None:
        print('Removing Shorts:')
        driver = self.driver
        shorts_master_containers = driver.find_elements(By.TAG_NAME, 'yt-horizontal-list-renderer')
        for _shorts_master_container in shorts_master_containers:
            self.load_all_shorts(shorts_container=_shorts_master_container)
            self.__delete_shorts_in_container(shorts_master_container=_shorts_master_container)

    def load_all_shorts(self, shorts_container: WebElement):
        _short_load_try_max = 100
        for _ in range(_short_load_try_max):
            try:
                press_arrow(shorts_container, "right")
            except Exception:
                break
        
        for _ in range(_short_load_try_max):
            try:
                press_arrow(shorts_container, "left")
            except Exception:
                    break

    def __delete_shorts_in_container(self, shorts_master_container: WebElement):
        """Remove all the shorts from a Container w/ a collection of shorts

        Args:
            shorts_master_container (WebElement): Container containing a collection of shorts
        """
        shorts_containers = shorts_master_container.find_elements(By.TAG_NAME, 'ytd-reel-item-renderer')
        for _shorts_container in shorts_containers:
            # Confirm shorts can be removed
            shorts_title: str = ic(_shorts_container.text.split('\n')[0])
            if shorts_title.strip() == 'All views of this video removed from history':
                continue
            
            print(f"\t- {shorts_title}...", end='')
            try:
                self.__remove_shorts(_shorts_container)
            except ElementNotInteractableException:
                press_arrow(shorts_master_container, "right")
                self.__remove_shorts(_shorts_container)
            
            self.removed_shorts.append(shorts_title)
            print("Removed.")

    def print_summary(self):
        print("="*50)
        print("\nSummary:")
        print(f"A total of {len(self.removed_videos)} videos and {len(self.removed_shorts)} shorts were removed.\n")
        print('Removed Videos:')
        for video in self.removed_videos:
            print(f"\t- {video}")
        print('\nRemoved Shorts:')
        for shorts in self.removed_shorts:
            print(f"\t- {shorts}")
                
    def __del__(self) -> None:
        del self.chrome
        #self.print_summary()
        #self.write_scrublist()
        
    def write_scrublist(self) -> None:
        for each in (self.channel_blacklist, self.channel_whitelist, 
                        self.keywords_blacklist, self.keywords_whitelist):
            
            # Remove duplicates using set()
            keywords = list(set(each.items))

            # Sort the list alphabetically using sorted()
            keywords = sorted(keywords)

            with open(each.path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(keywords))
                
    def __remove_shorts(self, shorts_container: WebElement) -> None:
            """
            Removes the shorts container passed to the function
            """
            for button in shorts_container.find_elements(By.TAG_NAME, "button"): 
                if button.get_attribute('aria-label') == 'Action menu':
                    if button.is_enabled():
                        button.click()
                        time.sleep(2)
                    break

            # Click Remove from watch history
            elements = self.driver.find_elements(By.TAG_NAME, "ytd-menu-service-item-renderer")
            button = self.chrome.find_element_by_text(elements, 'Remove from watch history')

            if button:
                button.click()
                time.sleep(2)

        
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

def press_arrow(shorts_master_container: WebElement, 
                direction: Literal['left', 'right']) -> None:
    """Press Arrow in Shorts Container

    Args:
        shorts_master_container (WebElement): Shorts Master Container Element
        direction (Literal["left", "right"]): Direction to click
    """
    direction = direction.lower().strip()
    _ = (
        shorts_master_container
        .find_element(By.ID, f"{direction}-arrow")
        .find_element(By.TAG_NAME, 'ytd-button-renderer')
        .click()
        )
    time.sleep(1)
    
