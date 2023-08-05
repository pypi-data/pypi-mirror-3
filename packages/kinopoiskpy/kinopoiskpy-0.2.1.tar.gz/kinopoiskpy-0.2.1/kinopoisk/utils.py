# -*- coding: utf-8 -*-
from parser import UrlRequest
from BeautifulSoup import BeautifulSoup
import re

class Manager(object):

    kinopoisk_object = None
    search_url = None

    def search(self, query):
        url, params = self.get_url_with_params(query)
        request = UrlRequest(url, params)
        content = request.read()
        # request is redirected to main page of object
        if request.is_redirected:
            instance = self.kinopoisk_object()
            instance.parse('main_page', content)
            return [instance]
        else:
            # <h2 class="textorangebig" style="font:100 18px">К сожалению, сервер недоступен...</h2>
            if content.find('<h2 class="textorangebig" style="font:100 18px">') != -1:
                return []
            content_results = content[content.find('<div class="search_results">'):content.find('<div style="height: 40px"></div>')]
            if content_results:
                soup_results = BeautifulSoup(content_results)
                # <div class="element width_2">
                results = soup_results.findAll('div', attrs={'class': re.compile('element')})
                if not results:
                    raise ValueError('No objects found in search results by request "%s"' % request.url)
                instances = []
                for result in results:
                    instance = self.kinopoisk_object()
                    instance.parse('link', unicode(result))
                    if instance.id:
                        instances += [instance]
                return instances

            raise ValueError('Unknown html layout found by request "%s"' % request.url)

    def get_url_with_params(self, query):
        return ('http://www.kinopoisk.ru/index.php', {'kp_query': query})

    def get_first(self, query):
        self.search(query)

#        htmlf=html[html.find(u'<!-- результаты поиска -->'):html.find(u'<!-- /результаты поиска -->')]
#        if htmlf<>"":
#            htmlf = htmlf[htmlf.find(u'Скорее всего вы ищете'):htmlf.find('</a>')]
#            htmlf=re.compile(r'<a class="all" href="(.+?)">').findall(htmlf)
#            try:
#                html = UrlRequest("http://www.kinopoisk.ru"+htmlf[0]).read()
#            except urllib2.URLError, why:
#                return None
#                exit

class KinopoiskObject(object):

    id = None
    objects = None

    _urls = {}
    _sources = []
    _source_classes = {}

    def __init__(self, id=None):
        if id:
            self.id = id

    def parse(self, name, content):
        self.get_source_instance(name).parse(self, content)

    def get_content(self, name):
        self.get_source_instance(name).get(self)

    def register_source(self, name, class_name):
        try:
            self.set_url(name, class_name.url)
        except:
            pass
        self.set_source(name)
        self._source_classes[name] = class_name

    def set_url(self, name, url):
        self._urls[name] = url

    def get_url(self, name):
        url = self._urls.get(name)
        if not url:
            raise ValueError('There is no urlpage with name "%s"' % name)
        if not self.id:
            raise ValueError('ID of object is empty')
        return 'http://www.kinopoisk.ru' + url % self.id

    def set_source(self, name):
        if name not in self._sources:
            self._sources += [name]

    def get_source_instance(self, name):
        class_name = self._source_classes.get(name)
        if not class_name:
            raise ValueError('There is no source with name "%s"' % name)
        return class_name()

class KinopoiskPage(object):

    def prepare_str(self, value):
        value = re.compile(r"&nbsp;").sub(" ", value)
        value = re.compile(r"&#151;").sub(" - ", value)
        value = re.compile(r"&#133;").sub("...", value)
        value = re.compile(r"<br>").sub("\n", value)
        value = re.compile(r"<.+?>").sub("", value)
        value = re.compile(r"&.aquo;").sub("\"", value)
        value = re.compile(r", \.\.\.").sub("", value)
        return value.strip()

    def prepare_int(self, value):
        value = self.prepare_str(value)
        value = int(value)
        return value

    def cut_from_to(self, content, after, before):
        start = content.find(after)
        end = content.find(before)
        if start != -1 and end != -1:
            content = content[start:end]
        return content

    def get(self, instance):
        raise NotImplementedError('This method must be implemented in subclass')

    def parse(self, instance, content):
        raise NotImplementedError('You must implement KinopoiskPage.parse() method')