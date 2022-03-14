from requests.exceptions import ConnectionError
import requests
import logging

class Download:
    def __init__(self, user_agent = 'wswp', timeout = 60):
        self.timeout = timeout
        self.headers = {'User-Agent' : user_agent}

    def download(self, url):
        logging.basicConfig(level = logging.ERROR)
        self.n_retries = 3
        print('Downloading ', url)
        try:
            resp = requests.get(url)
            html = resp.text
            status = resp.status_code
            if status >= 400:
                logging.ERROR(f'fail to acces {url}')
        except (Exception) as e:
            print('Error downloading', e)
            html = ''
        return html


        