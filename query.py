import re
from googlesearch import search
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def Search(query, start, stop):
    links = []
    for result in search(query, start = start, stop = stop, pause = 2):
        links.append(result)
    return links

def find_shops(link, html):    
    links = []
    shops = set()
    candidates = set()
    pattern = re.compile('(shop|store|vegan|market)', re.IGNORECASE)
    parsed_url = urlparse(link)
    if not html:
        try:
            if re.search(pattern, link).group(0):
                shops.add(link) #Is it better to add link t shops or candidates?
                return candidates, shops
        except AttributeError:
            return candidates, shops

    soup = BeautifulSoup(html, 'html.parser')
    link_elements = soup.find_all('a')  
    for element in link_elements:
        href = element.get('href')
        if href is None:
            continue
        if href.startswith('#'):
            continue
        if href.startswith('mailto'):
            continue
        if not href.startswith('http'):
            href_scheme = parsed_url.scheme
            href_netloc = parsed_url.netloc
            href_path = urljoin(parsed_url.path, href)
            href = f'{href_scheme}://{href_netloc}/{href_path}'
        links.append(href)
    if not links:
        return candidates, shops
    #Check if URL shop pattern is in entry link
    try:
        #Check wether pattern is found in URL
        if re.search(pattern, link).group(0):
            #Check wether pattern is found in URL's netloc 
            if re.search(pattern, parsed_url.netloc).group(0):
                link = f'{parsed_url.scheme}://{parsed_url.netloc}'
                if link not in shops:
                    shops.add(link)
                for L in links:
                    parsed_L = urlparse(L)
                    if parsed_L.netloc == parsed_url.netloc:
                        continue
                    if re.search(pattern, parsed_L.path):
                        candidates.add(L)
                return candidates, shops
            #Check wether the pattern is found in URL's path
            elif re.search(pattern, parsed_url.path).group(0):
                #get the shortest path including pattern
                shortURL_pattern = re.compile('http[s]?://[\w.]*/\w*(shop|store|vegan|market)\w*/', re.ASCII)
                link = re.search(shortURL_pattern, link).group(0)
                if not link in shops:
                    shops.add(link)
                for L in links:
                    if re.search(pattern, L):
                        parsed_L = urlparse(L)
                        if parsed_L.netloc == parsed_url.netloc:
                            continue
                        candidates.add(L)
                return candidates, shops
                        
        for L in links:
            if re.search(pattern, L).group(0):
                if L not in candidates:
                    candidates.add(L)
            else:
                continue
        return candidates, shops

    except AttributeError:
            return candidates, shops










