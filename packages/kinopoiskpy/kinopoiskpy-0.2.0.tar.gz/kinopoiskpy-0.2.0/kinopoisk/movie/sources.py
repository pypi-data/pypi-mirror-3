# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from kinopoisk.utils import KinopoiskPage
from kinopoisk.parser import UrlRequest
import re

class MovieLink(KinopoiskPage):
    '''
    Parser movie info from links
    '''
    def parse(self, instance, content):
        content_soup = BeautifulSoup(content)

        link = content_soup.find('p', {'class': 'name'})
        if link:
            link = link.find('a')
            if link:
                # /level/1/film/342/sr/1/
                instance.id = self.prepare_int(link['href'].split('/')[4])
                instance.title = self.prepare_str(link.text)

        year = content_soup.find('p', {'class': 'name'})
        if year:
            year = year.find('span', {'class': 'year'})
            if year:
                instance.year = self.prepare_int(year.text)

        otitle = content_soup.find('span', {'class': 'gray'})
        if otitle:
            if u'мин' in otitle.text:
                values = otitle.text.split(', ')
                instance.runtime = self.prepare_int(values[-1].split(' ')[0])
                instance.title_original = self.prepare_str(', '.join(values[:-1]))
            else:
                instance.title_original = self.prepare_str(otitle.text)

        instance.set_source('link')

class MovieMainPage(KinopoiskPage):
    '''
    Parser of main movie page
    '''
    url = '/level/1/film/%d/'

    def parse(self, instance, content):
        instance_id = re.compile(r'<script type="text/javascript"> id_film = (\d+); </script>').findall(content)
        if instance_id:
            instance.id = self.prepare_int(instance_id[0])

        content_info = BeautifulSoup(content)
        title = content_info.find('h1', {'class': 'moviename-big'})
        if title:
            instance.title = self.prepare_str(title.text)

        title_original = content_info.find('span', {'style': 'color: #666; font-size: 13px'})
        if title_original:
            instance.title_original = self.prepare_str(title_original.text)

        # <div class="brand_words" itemprop="description">
        plot = content_info.find('div', {'class': 'brand_words', 'itemprop': 'description'})
        if plot:
            instance.plot = self.prepare_str(plot.text)

        table_info = content_info.find('table', {'class': 'info'})
        if table_info:
            for tr in table_info.findAll('tr'):
                tds = tr.findAll('td')
                name = tds[0].text
                value = tds[1].text

                if name == u'слоган':
                    instance.tagline = self.prepare_str(value)
                elif name == u'время':
                    instance.runtime = self.prepare_str(value)
                elif name == u'год':
                    instance.year = self.prepare_int(value)

        instance.set_source('main_page')

class MoviePostersPage(KinopoiskPage):
    '''
    Parser of movie posters page
    '''
    url = '/level/17/film/%d/'

    def get(self, instance):
        content = UrlRequest(instance.get_url('posters')).read()

        # header with sign 'No posters'
        if re.findall(r'<h1 class="main_title">', content):
            return False

        content = content[content.find('<div style="padding-left: 20px">'):content.find('        </td></tr>')]

        soup_content = BeautifulSoup(content)
        table = soup_content.findAll('table', attrs={'class': re.compile('^fotos')})
        if table:
            self.parse(instance, unicode(table[0]))
        else:
            raise ValueError('Parse error. Do not found posters for movie %s' % (instance.get_url('posters')))

    def parse(self, instance, content):
        links = BeautifulSoup(content).findAll('a')
        for link in links:
            img_id = re.compile(r'/picture/(\d+)/').findall(link['href'])
            try:
                img_id = int(img_id[0])
                if img_id not in instance.posters:
                    instance.posters += [img_id]
            except:
                pass

        instance.set_source('posters')

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)