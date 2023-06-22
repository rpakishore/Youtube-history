import typer
from pathlib import Path
from youtube_history import Scrubber
app = typer.Typer()

@app.command()
def scrub(
    keywords_blacklist: str = Path('keyword-blacklist.txt'), 
    keywords_whitelist: str = Path('keyword-whitelist.txt'), 
    channel_blacklist: str = Path('channel-blacklist.txt'), 
    channel_whitelist: str = Path('channel-whitelist.txt'), 
    close: bool = True):
    """Scrubs the videos/shorts from youtube history depending on the keyword lists provided
    \n
    Args:\n
        keywords_blacklist (str): Path to the keywords-blacklist file. Defaults to `keyword-blacklist.txt`\n\t
        keywords_whitelist (str): Path to the keywords-whitelist file. Defaults to `keyword-whitelist.txt`\n\t
        channel_blacklist (str): Path to the channel-blacklist file. Defaults to `channel-blacklist.txt`\n\t
        channel_whitelist (str): Path to the channel-whitelist file. Defaults to `channel-whitelist.txt`\n\t
        close (bool, optional): Close browser after scrubbing. Defaults to True.
    """
    keywords_blacklist = Path(str(keywords_blacklist))
    keywords_whitelist = Path(str(keywords_whitelist))
    channel_blacklist = Path(str(channel_blacklist))
    channel_whitelist = Path(str(channel_whitelist))

    scrub = Scrubber(
        keywords_blacklist=keywords_blacklist, 
        keywords_whitelist = keywords_whitelist, 
        channel_blacklist = channel_blacklist, 
        channel_whitelist = channel_whitelist)
    
    scrub.scrub_videos()
    scrub.scrub_shorts()
    
    if close:
        del scrub
