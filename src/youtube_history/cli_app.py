import typer
from pathlib import Path
from youtube_history import Scrubber
app = typer.Typer()

@app.command()
def scrub(
    keywords_blacklist: str = 'keyword-blacklist.txt', 
    keywords_whitelist: str = 'keyword-whitelist.txt', 
    channel_blacklist: str = 'channel-blacklist.txt', 
    channel_whitelist: str = 'channel-whitelist.txt', 
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
    keywords_blacklist: Path = Path(str(keywords_blacklist))
    keywords_whitelist: Path = Path(str(keywords_whitelist))
    channel_blacklist: Path = Path(str(channel_blacklist))
    channel_whitelist: Path = Path(str(channel_whitelist))

    scrub = Scrubber(
        keywords_blacklist=keywords_blacklist, 
        keywords_whitelist = keywords_whitelist, 
        channel_blacklist = channel_blacklist, 
        channel_whitelist = channel_whitelist)
    
    try:
        scrub.scrub_videos()
    except Exception as e:
        print(f'Error occured when scrubbing videos:\n{str(e)}')
    try:
        scrub.scrub_shorts()
    except Exception as e:
        print(f'Error occured when scrubbing shorts:\n{str(e)}')    
    
    scrub.print_summary()        
    if close:
        del scrub
