from query import Search, find_shops
from urllib.parse import urlparse
import time
from downloads import Download
import concurrent.futures

def process(link):
    D = Download()
    last_domain = None
    L = link
    Throttle(L, last_domain)
    html = D.download(L)
    last_domain = urlparse(L).netloc
    try:       
        candidates, shops = find_shops(L, html)
        return candidates, shops
    except TypeError:
        candidates, shops = set(), set()
        return candidates, shops
    
def Throttle(link, last_domain):
    if last_domain:
        if urlparse(link).netloc == last_domain:
            time.sleep(1) 

def main(query, n_results):
    start_time = time.time()
    shop_links = set()
    candidates_links = set()
    extract_from_candidates = False
    links = []
    start = 0
    stop = 5
    while len(shop_links) < n_results: 
        print('Len shop links =', len(shop_links) )
        if not links:
            if not extract_from_candidates  and candidates_links:
                print('Not links, EXTRACTING from candidates')
                extract_from_candidates = True
                if len(candidates_links) >= 5:
                    candidate = 0
                    while candidate < 5:
                        links.append(candidates_links.pop())
                        candidate += 1
                else:
                    candidate = 0
                    n_candidates = len(candidates_links)
                    while candidate < n_candidates:
                        links.append(candidates_links.pop())
                        candidate += 1
            elif not extract_from_candidates and not candidates_links or extract_from_candidates:
                print('Not links, EXTRACTING from google')
                links = [link for link in Search(query, start = start, stop = stop)]
                start += 6
                stop = start + 5
                time.sleep(5)
                if not extract_from_candidates:
                    extract_from_candidates = True
                if extract_from_candidates:
                    extract_from_candidates = False
        with concurrent.futures.ThreadPoolExecutor(max_workers = 10) as executor:
            if n_results - len(shop_links) >= 5:
                print('MORE tan 5 links to get 20')
                futures = [executor.submit(process, link) for link in links]
                links = []
                for data in concurrent.futures.as_completed(futures):
                    candidates, shops = data.result()
                    candidates_links = candidates_links | candidates
                    shop_links = shop_links | shops
            else:
                print('LESS tan 5 links to get 20')
                links_to_complete = n_results - len(shop_links)
                if links_to_complete > len(links):
                    futures = [executor.submit(process, link) for link in links]
                    links = []
                    for data in concurrent.futures.as_completed(futures):
                        candidates, shops = data.result()
                        candidates_links = candidates_links | candidates
                        shop_links = shop_links | shops

                else:
                    count = 0
                    futures = []
                    while count <= links_to_complete:
                        link = links.pop()
                        future = executor.submit(process, link)
                        futures.append(future)
                        count += 1
                    for data in concurrent.futures.as_completed(futures):
                        candidates, shops = data.result()
                        candidates_links = candidates_links | candidates
                        shop_links = shop_links | shops

    print('Total time: %ss' % (time.time() - start_time))
    return list(shop_links)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', default=None,
                         type = str, help = 'Query string to make the search on')
    parser.add_argument('-n', default = 20, type = int, help = 'Number of spected links to retrieve')
    parser.add_argument('-o', default= 'links.txt',
                         type= argparse.FileType('w'), help= 'output file to print on')
    args = parser.parse_args()
    l_shops = main(args.q, args.n)
    print(l_shops, file= args.o)
        
