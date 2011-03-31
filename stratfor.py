#!/usr/bin/env  python
__license__   = 'GPL v3'
__copyright__ = '2011, unnamedrambler@gmail.com'
__docformat__ = 'restructuredtext en'

from calibre.web.feeds.news import BasicNewsRecipe
import copy, re


class Stratfor(BasicNewsRecipe):

    title                  = 'Stratfor'
    __author__             = ''
    description            = 'Global Intelligence'
    needs_subscription     = True
    max_articles_per_feed  = 100
    no_stylesheets         = True
    encoding               = 'utf8'
    publisher              = 'Stratfor'
    category               = 'news, intelligence, world'
    language               = 'en'
    publication_type       = 'newspaper'

    timefmt  = '%B %d, %Y %H%M %Z'

    extra_css      = '''h1{color:#093D72 ; font-family:Georgia,"Century Schoolbook","Times New Roman",Times,serif; }
                    h2, .section-title {color:#474537; font-family:Georgia,"Century Schoolbook","Times New Roman",Times,serif; font-style:italic;}
                    .submitted{color:gray; font-family:Georgia,"Century Schoolbook","Times New Roman",Times,serif; font-size:small; font-style:italic;}
                    .insettipUnit {color:#666666; font-family:Arial,Sans-serif;font-size:xx-small }
                    .media-caption, .media-copyright{ font-size:x-small; color:#333333; font-family:Arial,Helvetica,sans-serif}
                    .article{font-family :Arial,Helvetica,sans-serif; font-size:x-small}
                    .tagline {color:#333333; font-size:xx-small}
                    .dateStamp {color:#666666; font-family:Arial,Helvetica,sans-serif}
                        h3{font-family:Arial,Helvetica,sans-serif;}
                        .byline{color:blue;font-family:Arial,Helvetica,sans-serif; font-size:xx-small}
                        h6{color:#333333; font-family:Georgia,"Century Schoolbook","Times New Roman",Times,serif; font-style:italic; }'''

    remove_tags_before = dict(id='content-inner')
    remove_tags = [
                    dict(id=["text-resize-bar", ]),
                    {'class':["facebook_like", "stratfor_feedback", "toplink-wrapper", "share_this_container", "relatedlinks" ]},
                    dict(rel='shortcut icon'),
                    ]
    remove_tags_after = [{'class':"content"},]

    def get_browser(self):
        br = BasicNewsRecipe.get_browser()
        if self.username is not None and self.password is not None:
            br.open('http://www.stratfor.com/user')
            br.select_form(nr=0)
            br['name']   = self.username
            br['pass'] = self.password
            res = br.submit()
            raw = res.read()
            if 'My Account' not in raw:
                raise ValueError('Failed to log in to stratfor.com, check your '
                        'username and password')
        return br

    def parse_articles(self, soup):
        articles = []
        for div in soup.findAll(True, attrs={'class':['node-teaser']}):
            a = div.find('a', href=True)
            if not a:
                continue
            url = re.sub(r'\?.*', '', a['href']).strip()
            
            title_div = div.find('div', attrs={'class':['teaser-title']})
            if title_div:
                title = title_div.find('h2', text=True).strip()
            if not title:
                continue

            img = div.find('img')
            if img:
                img_url = img['src'].strip()

            date_div = div.find('div', attrs={'class':['teaser-timestamp']})
            if date_div:
                pubdate = self.tag_to_string(date_div, use_alt=False).strip()

            desc_div = div.find('div', attrs={'class':['teaser-text']})
            if desc_div:
                description = self.tag_to_string(desc_div, use_alt=False).replace("[more]", "")

            d = dict( title=title, url=url, description=description, date=pubdate, content ='')
            articles.append( d )
        return articles

    def parse_index(self):
        feeds = { 'Analysis':'http://www.stratfor.com/analysis', 'Geopolitical Diary':'http://www.stratfor.com/geopolitical_diary', 'Situation Reports': 'http://www.stratfor.com/situation_reports'}
        weights = { 'Analysis':1, 'Geopolitical Diary':2, 'Situation Reports': 3}
        articles = {}
        categories = feeds.keys()
        for key,url in feeds.iteritems():
            print "Downloading %s " %(key)
            soup = self.index_to_soup(url)
            articles[key] = self.parse_articles(soup)
            print "Got %s articles from %s " %(len(articles), key)
            print articles

        categories = self.sort_index_by(categories, weights)
        categories = [(key, articles[key]) for key in categories if articles.has_key(key)]
        return categories

    def postprocess_html(self, soup, first):
        for tag in soup.findAll(name=['table', 'tr', 'td']):
            tag.name = 'div'

        for tag in soup.findAll('div', dict(id=["articleThumbnail_1", "articleThumbnail_2", "articleThumbnail_3", "articleThumbnail_4", "articleThumbnail_5", "articleThumbnail_6", "articleThumbnail_7"])):
            tag.extract()

        return soup

    def get_masthead_url(self):
        return "http://www.stratfor.com/sites/all/themes/zen/stratfor/images/header_BKG.jpg"

    def cleanup(self):
        self.browser.open('http://www.stratfor.com/logout')

