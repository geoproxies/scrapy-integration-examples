import os
import sys
sys.path.append(os.getcwd())

import scrapy
import json
from bs4 import BeautifulSoup
from geoproxies import ProxySettings


class NationalitySpider(scrapy.Spider):
    name = "nationality"

    def __init__(self):
        self.params = {}
        # Please, replace the token value below, with your Geoproxies account token
        self.proxy_settings = ProxySettings(
            token="7ce374a3-5616-44b1-9fed-6746c86c3e5d")

    def start_requests(self):
        u = 'http://rdrct.info/geo.php'
        yield scrapy.Request(u, callback=self.parse, meta=dict(proxy=str(self.proxy_settings.new_tracking_id())), dont_filter=True)

    def parse(self, response):
        if 'mission' in response.meta:
            if self.params['mission'] == 'get-nationality':
                soup = BeautifulSoup(response.text, "lxml")
                for table in soup.select('table'):
                    for tr in table.find_all('tr'):
                        tds = tr.find_all('td')
                        if len(tds) == 3:
                            if tds[0].get_text().lower() == self.params['country'].lower():
                                print("You are " + tds[2].get_text())
                                print("\n\n\n\n")

            elif response.meta['mission'] == 'get-country':
                r = json.loads(response.text)
                self.params['mission'] = 'get-nationality'
                self.params['country'] = r[self.params['country-code']]

                return self.get_nationality(response)
        else:
            r = json.loads(response.text)
            self.params['mission'] = 'get-country'
            self.params['country-code'] = r['country']

            return self.country_names(response)

    def get_nationality(self, response):
        req = response.follow(
            'https://www.myenglishpages.com/site_php_files/vocabulary-lesson-countries-nationalities.php', self.parse, meta=dict(proxy=str(self.proxy_settings.new_tracking_id())))
        self.update_params(req)
        yield req

    def country_names(self, response):
        req = response.follow('http://country.io/names.json', self.parse,
                              meta=dict(proxy=str(self.proxy_settings.new_tracking_id())))
        self.update_params(req)
        yield req

    def update_params(self, request):
        request.meta.update(self.params)
