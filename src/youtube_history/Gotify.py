import requests

from .logger import log
from .credentials import get_password

log.debug('Sending No')

def notify(title: str, message: str="", priority: int=2, 
            apptoken: str|None=None, url: str = 'https://gotify.rpakishore.co.in', app: str= 'HomeServer') -> None:
    log.debug(f'Sending message {title} to {app} with priority:{priority}')
    resp = requests.post(f"{url}/message?token={get_password('gotify', app) if apptoken is None else apptoken}",
                            json={
                                "message": message,
                                "priority": priority,
                                "title": title
                            })
    log.info(f'[GOTIFY]Response: {resp}')
