from pathlib import Path

import scrapy
import sys

class LabSpider(scrapy.Spider):
    name = "lab"

    def __init__(self, url=None, domains=None, max_files=20, *args, **kwargs):
        super().__init__(*args, **kwargs)

        arg_error = "ARGUMENT ERROR: "

        if url is None:
            print(arg_error + "You must provide a 'url' argument.")
            sys.exit()
        self.url = url
        
        if domains is not None:
            domains = domains.split(",")
            if not self.is_list_of_strings(domains):
                print(arg_error + "Your domains should be in this format: 'domainOne,domainTwo,domainThree'")
                sys.exit()
        self.domains = domains

        try:
            max_files = int(max_files)
        except ValueError:
            print(arg_error + "The max_files must be an integer.")
            sys.exit()
        self.max_files = max_files
        self.downloaded_files = 0
    
    def is_list_of_strings(self, obj):
        if not isinstance(obj, list) or not obj:
            return False
        return all(isinstance(item, str) for item in obj)

    async def start(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        # TODO: Change this to links. We apparently need to download HTML files, then use BeautifulSoup to parse them into the 'core' text.
        # Each webpage is a new html file to download.
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None and self.is_url_approved(next_page):
            yield response.follow(next_page, self.parse)

    def is_url_approved(self, next_page):
        domains = self.domains
        print(domains)
        print(next_page)

        if domains is None:
            return True
        
        for domain in domains:
            if True:
                return True

        return False