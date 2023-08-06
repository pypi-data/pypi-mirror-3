# encoding: utf-8

import unittest
import opengraph


HTML = """
<html xmlns:og="http://ogp.me/ns#">
<head>
<title>The Rock (1996)</title>
<meta property="og:title" content="The Rock" />
<meta property="og:type" content="movie" />
<meta property="og:url" content="http://www.imdb.com/title/tt0117500/" />
<meta property="og:image" content="http://ia.media-imdb.com/images/rock.jpg" />
</head>
</html>
"""

class test(unittest.TestCase):
    def test_url(self):
        data = opengraph.OpenGraph(url='http://vimeo.com/896837')
        self.assertEqual(data.items['url'], 'http://vimeo.com/896837')
        
    def test_isinstace(self):
        data = opengraph.OpenGraph()
        self.assertTrue(isinstance(data,opengraph.OpenGraph))
        
    def test_to_html(self):
        og = opengraph.OpenGraph(html=HTML)
        self.assertTrue(og.to_html())
        
    def test_is_valid(self):
        og = opengraph.OpenGraph(url='http://grooveshark.com')
        self.assertTrue(og.is_valid())

    def test_is_not_valid(self):
        og = opengraph.OpenGraph(url='http://vdubmexico.com')
        self.assertFalse(og.is_valid())
    
    def test_required(self):
        og = opengraph.OpenGraph(url='http://grooveshark.com', required_attrs=("description",), scrape=True)
        self.assertTrue(og.is_valid())
    
    def test_scrape(self):
        og = opengraph.OpenGraph(url='http://graingert.co.uk/', required_attrs=("description",), scrape=True)
        self.assertTrue(og.is_valid())
        self.assertTrue(og.items["description"])

    
if __name__ == '__main__':
    unittest.main()
