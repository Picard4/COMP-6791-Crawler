from pathlib import Path

import scrapy
import sys
import re
import os
import tldextract
import math
from scrapy.linkextractors import LinkExtractor

class LabSpider(scrapy.Spider):
    name = "lab"

    handle_httpstatus_list = [503]

    def __init__(self, url=None, domains=None, max_files=20, link_limit=math.inf, *args, **kwargs):
        super().__init__(*args, **kwargs)

        arg_error = "ARGUMENT ERROR: "

        if url is None:
            print(arg_error + "You must provide a 'url' argument.")
            sys.exit()
        self.url = url
        
        self.domains = None
        if domains is not None:
            domains = domains.split(",")
            if not self.is_list_of_strings(domains):
                print(arg_error + "Your domains should be in this format: 'domainOne,domainTwo,domainThree'")
                sys.exit()
            self.domains = domains
            if not self.is_url_approved(url):
                print(arg_error + "Your starting url is not approved by your sent domain list!")
                print("Your starting url: " + url)
                print("Your starting url's domain: " + tldextract.extract(url).domain)
                print("Your domain list: " + str(domains))
                sys.exit()

        try:
            self.max_files = int(max_files)
        except ValueError:
            print(arg_error + "The max_files must be an integer.")
            sys.exit()
        if self.max_files < 1:
            print(arg_error + "Minimum value for max_files is 1.")
            sys.exit()

        self.link_limit = link_limit
        if link_limit != math.inf:
            try:
                self.link_limit = int(link_limit)
            except ValueError:
                print(arg_error + "The link_limit must be an integer.")
                sys.exit()
            if self.link_limit < 0:
                print(arg_error + "Minimum value for link_limit is 0.")
                sys.exit()

        self.link_list = [url]
        self.link_extractor = LinkExtractor()
        self.next_link_index = 0
        self.files_downloaded = 0

        self.output_dir = "HTML-Files"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    
    def is_list_of_strings(self, obj):
        if not isinstance(obj, list) or not obj:
            return False
        return all(isinstance(item, str) for item in obj)

    async def start(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        if response.status in self.handle_httpstatus_list:
            print(f"HTTP Error {response.status} from {self.link_list[self.next_link_index]}. Moving on to the next link if possible.")
            self.next_link_index += 1
            if self.next_link_index < len(self.link_list):
                print(f"New link found with {self.link_list[self.next_link_index]}. Resuming crawling...")
                yield response.follow(self.link_list[self.next_link_index], self.parse)
            else:
                print("Out of links. Crawling stops here.")
                return
        
        # Save the webpage as an HTML file.
        encoding = 'utf-8'
        html_content = response.body.decode(encoding, errors='ignore')
        filename = f'File{self.files_downloaded + 1}-{re.sub(r"[#%&{}\\<>*?/ $!'\":@+`|=.]", '_', response.url)}.html'
        with open(os.path.join(self.output_dir, filename), 'w', encoding=encoding) as f:
            f.write(html_content)
            print("Saved new file: " + filename)
            self.files_downloaded += 1

        # Add some new links on the page to the link_list.
        # There is an optional limit to how many links can be added per page.
        if self.link_limit > 0:
            links_added = 0
            try:
                for link in self.link_extractor.extract_links(response):
                    if link.url not in self.link_list and self.is_url_approved(link.url):
                        self.link_list.append(link.url)
                        links_added += 1
                        if links_added >= self.link_limit:
                            break
            except Exception as e:
                print(f"An error occurred while parsing for links - no new links will be saved from {self.link_list[self.next_link_index]}")
                print(e)
        
        # Advance to the next link... if there is one in the link_list.
        self.next_link_index += 1
        if self.next_link_index < len(self.link_list) and self.files_downloaded < self.max_files:
            yield response.follow(self.link_list[self.next_link_index], self.parse)

    def is_url_approved(self, url):
        if self.domains is None:
            return True
        
        extracted_url = tldextract.extract(url)
        for trusted_domain in self.domains:
            if trusted_domain.casefold() == extracted_url.domain.casefold():
                return True

        return False