import typer
from pathlib import Path
from youtube_history import Scrubber
app = typer.Typer()

@app.command()
def scrub(
    keywords_file: str = Path('scrublist.txt'), 
    close: bool = True):
    """Scrubs the videos/shorts from youtube history depending on the keyword list provided

    Args:
        keywords_file (str): Path to the keywords file. Defaults to `scrublist.txt`
        close (bool, optional): Close browser after scrubbing. Defaults to True.
    """
    if keywords_file:
        keywords_file = Path(str(keywords_file))

    scrub = Scrubber(
        keywords_file=keywords_file
    )
    scrub.scrub_videos()
    scrub.scrub_shorts()
    
    if close:
        del scrub

