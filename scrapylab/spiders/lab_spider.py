from pathlib import Path

import scrapy
import sys
import re
import os
import tldextract
from scrapy.linkextractors import LinkExtractor

class LabSpider(scrapy.Spider):
    name = "lab"

    def __init__(self, url=None, domains=None, max_files=20, *args, **kwargs):
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

        self.link_list = [url]
        self.link_extractor = LinkExtractor()
        self.next_link_index = 0

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
        # Save the webpage as an HTML file.
        encoding = 'utf-8'
        html_content = response.body.decode(encoding, errors='ignore')
        filename = f'File{self.next_link_index + 1}-{re.sub(r"[#%&{}\\<>*?/ $!'\":@+`|=.]", '_', response.url)}.html'
        with open(os.path.join(self.output_dir, filename), 'w', encoding=encoding) as f:
            f.write(html_content)
            print("Saved new file: " + filename)

        # Add any new links on the page to the link_list.
        # The link_list has a max capacity (max_files) - stop adding links if this capacity is reached.
        if len(self.link_list) < self.max_files:
            for link in self.link_extractor.extract_links(response):
                if link.url not in self.link_list and self.is_url_approved(link.url):
                    self.link_list.append(link.url)
                    if len(self.link_list) >= self.max_files:
                        break
        
        # Advance to the next link... if there is one in the link_list.
        self.next_link_index += 1
        if self.next_link_index < len(self.link_list):
            yield response.follow(self.link_list[self.next_link_index], self.parse)

    def is_url_approved(self, url):
        if self.domains is None:
            return True
        
        extracted_url = tldextract.extract(url)
        for trusted_domain in self.domains:
            if trusted_domain.casefold() == extracted_url.domain.casefold():
                return True

        return False