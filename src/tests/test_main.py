import pytest
from youtube_history.main import Scrubber, Keywords, VideoInfo

@pytest.fixture
def scrubber():
    return Scrubber(
        keywords_blacklist='keyword-blacklist.txt',
        keywords_whitelist='keyword-whitelist.txt',
        channel_blacklist='channel-blacklist.txt',
        channel_whitelist='channel-whitelist.txt'
    )

@pytest.fixture
def video_element():
    # Mocking WebElement
    class MockElement:
        def __init__(self):
            self.title = 'Test Video'
            self.channel = 'Test Channel'
            self.description = 'Test Description'
            
        def find_element(self, *args):
            if args[0] == 'title-wrapper':
                return MockElement()
            elif args[0] == 'metadata':
                return MockElement()
            elif args[0] == 'channel-name':
                return MockElement()
            elif args[0] == 'description-text':
                return MockElement()
        
        def text(self):
            return 'Test Video Test Channel Test Description'.lower()
        
    return MockElement()

def test_scrub_videos(scrubber, video_element):
    scrubber.driver.find_elements = lambda *args: [video_element]
    scrubber.scrub_videos()
    # Add your assertions here

def test_video_info(video_element):
    video_info = VideoInfo(video_element)
    # Add your assertions here

def test_to_remove(video_element):
    video_info = VideoInfo(video_element)
    # Add your assertions here

def test_write_scrublist(scrubber, tmp_path):
    scrubber.channel_blacklist.path = tmp_path / 'channel-blacklist.txt'
    scrubber.keywords_blacklist.path = tmp_path / 'keyword-blacklist.txt'
    scrubber.write_scrublist()
    # Add your assertions here

def test_get_keywords(tmp_path):
    filepath = tmp_path / 'test_keywords.txt'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('Keyword1\nkeyword2\nkeyword3\n')
    keywords = get_keywords(filepath)
    assert keywords == ['keyword1', 'keyword2', 'keyword3']
