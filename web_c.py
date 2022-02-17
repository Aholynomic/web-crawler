import requests, sys, argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from time import perf_counter

import requests.exceptions

"""
TODO
include rules for robots.txt
detect duplicates google.com/ and google.com
check python version
save results to excel file
modify web headers - uAgent
add exceptions for just domain names
"""

userAgent = "*"

class WebCrawler():
    
    def __init__(self, url, max_crawl=1) -> None: 
        """Constructor for Web Crawler

        Args:
            url: Base URL for starting point
            max_crawl: maximum number of URL's to be crawled (default is 1)

        Returns:
            None
        """

        self.start_url = url # (needed args)
        self.max = max_crawl # (optional)
    
        # have list of urls to visit
        self.tasks = []
        self.tasks.append(url)

        # visited urls
        self.visited = []

        # ensure same domain
        self.domain = "https://" + urlparse(url).netloc

    def crawl(self):
        """Check robots.txt for rules and add URL links to a queue and sends web requests to those links

        Returns: 
            None
        """
        
        while(len(self.tasks) > 0 and len(self.visited) < self.max):
            # grab the url from the queue
            next_url = self.tasks.pop(0)
            
            # check if it has been visited before to avoid duplicates
            if next_url not in self.visited:
                
                print("Parsing: {}".format(next_url))
                
                try:
                    # add to visited links
                    self.visited.append(next_url)

                    # send web request to the url
                    page_content = requests.get(next_url).text

                    # parse the html and find data
                    self.parse(next_url, page_content)

                    # raise for exception, continue if successful
                    #page_content.raise_for_status()
                    
                except KeyboardInterrupt:
                    print("Program Cancelled.")
                    sys.exit(0)
                except requests.exceptions.HTTPError as httpErno:
                    print("FAILED: {}".format(next_url))
                    print("HTTP Error: {}".format(httpErno))
                except requests.exceptions.ConnectionError as connErno:
                    print("FAILED: {}".format(next_url))
                    print("Error Connecting: {}".format(connErno))
                except requests.exceptions.Timeout as timeErno:
                    print("FAILED: {}".format(next_url))
                    print("Timeout Error: {}".format(timeErno))
                except requests.exceptions.RequestException as reqErno:
                    print("FAILED: {}".format(next_url))
                    print("Unknown Error: {}".format(reqErno))   
                else:
                    print("************** COMPLETED: {}".format(next_url))
            
            

    def parse(self, url, page_content):
        """Parse the html using Beautful Soup and 
        find all links which are added to a queue

        Args:
            url: the link that will be crawled
            page_content: the raw html
        
        Returns:
            None
        """

        # parse using Beautiful Soup
        soup = BeautifulSoup(page_content, "html.parser")
                
        # find titles in html (TODO)
        title = soup.find("title")

        print("*** URL's found in: {}".format(url))

        # find all <a> tags
        urls = soup.find_all("a")
        for url in urls:
            
            # find all href attr with those tags
            url = url.get("href")
            
            try:
                # check if it exists
                if url is not None:
                    # check if in domain
                    if url.startswith(self.domain):
                        # if not in tasks
                        if url not in self.tasks:
                            # if not visited
                            if url not in self.visited:
                                print("**************: {}".format(url))
                                self.tasks.append(url)     
            except:
                pass
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A basic web crawler.')
    requiredArgs = parser.add_argument_group("required named arguments")
    requiredArgs.add_argument("-H", "--host", required=True, type=str, dest="host", help="Destination URL")

    parser.add_argument("-m", "--max", type=int, default=1, dest="max", help="Max number of URL's to crawl (Default is 1)")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="Suppress Output")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verb", help="Verbose Output")
    args = parser.parse_args()

    test = WebCrawler(args.host, args.max)
    start_time = perf_counter()
    test.crawl()
    end_time = perf_counter()
    print("Time taken: {}".format(str(end_time - start_time)) + " seconds.")  