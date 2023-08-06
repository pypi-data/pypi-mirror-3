# encoding: utf-8

import re
import urllib2
from BeautifulSoup import BeautifulSoup

class OpenGraph(object):
    """
    """

    required_attrs = set(('title', 'type', 'image', 'url'))
    scrape = False

    def __init__(self, url=None, html=None, scrape=False, **kwargs):
        # If scrape == True, then will try to fetch missing attribtues
        # from the page's body
        self.scrape = scrape
        self.url = url
        self.items = {}
                
        if url is not None:
            self.fetch(url)
            
        if html is not None:
            self.parser(html)
            
    def fetch(self, url):
        """
        """
        raw = urllib2.urlopen(url)
        html = raw.read()
        return self.parser(html)
        
    def parser(self, html):
        """
        """
        if not isinstance(html,BeautifulSoup):
            doc = BeautifulSoup(html)
        else:
            doc = html
        ogs = doc.html.head.findAll(property=re.compile(r'^og'))
        for og in ogs:
            if og.has_key(u'content'):
                self.items[og[u'property'][3:]]=og[u'content']

        # Couldn't fetch all attrs from og tags, try scraping body
        remaining_keys = self.required_attrs - set(self.items.viewkeys())
        
        for key in remaining_keys:
            try:
                self.items[key] = getattr(self, 'scrape_%{key}'.format(key=key))(doc)
            except AttributeError:
                pass
        
    def is_valid(self):
        return self.required_attrs <= set(self.items.viewkeys())
        
    def to_html(self):
        if not self.is_valid():
            return u"<meta property=\"og:error\" content=\"og metadata is not valid\" />"
            
        meta = u""
        for key,value in self.items.iteritems():
            meta += u"\n<meta property=\"og:%s\" content=\"%s\" />" %(key, value)
        meta += u"\n"
        
        return meta
        
    def scrape_image(self, doc):
        images = [dict(img.attrs)['src'] 
            for img in doc.html.body.findAll('img')]

        if images:
            return images[0]

        return u''

    def scrape_title(self, doc):
        return doc.html.head.title.text

    def scrape_type(self, doc):
        return 'other'

    def scrape_url(self, doc):
        return self._url
