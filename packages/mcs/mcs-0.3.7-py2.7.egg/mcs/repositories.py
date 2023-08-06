from __future__ import with_statement
import base64
import HTMLParser
import httplib2
import logging
import os
import urlparse
import urllib

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
log = logging.getLogger('mcs')


class LinkExtractor(HTMLParser.HTMLParser):
    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self.links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(value for name, value in attrs if name == "href")


class RepositoryException(Exception):
    pass


class McRepository(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError
    
    def list_items(self):
        raise NotImplementedError
    
    def load_item(self, name):
        raise NotImplementedError
    
    def store_item(self, name, data):
        raise NotImplementedError
    
    def _filter_items(self, item_list):
        return [name for name in item_list if name.endswith(".mcz")
                                              or name.endswith(".mcd")]
    
    @staticmethod
    def for_url(url):
        if url.startswith("http:") or url.startswith("https:"):
            return McHttpRepository(url)
        elif url.partition(":")[0] in McHttpRepositoryShortcut.locations:
            return McHttpRepositoryShortcut(url)
        return McLocalRepository(url)


class McLocalRepository(McRepository):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        assert os.path.exists(self.path) and os.path.isdir(self.path), "'%s' does not exist or is not a directory." % self.path
    
    def list_items(self):
        return self._filter_items(os.listdir(self.path))
    
    def load_item(self, name):
        with file(os.path.join(self.path, name), "rb") as f:
            return f.read()
    
    def store_item(self, name, data):
        with file(os.path.join(self.path, name), "wb") as f:
            f.write(data)


class McHttpRepository(McRepository):
    def __init__(self, url):
        self.http = httplib2.Http()
        self.additional_headers = dict()
        
        urlsplit = urlparse.urlsplit(url)
        if urlsplit.username or urlsplit.password:
            self.url = urlparse.urlunsplit([
                urlsplit[0], 
                urlsplit.hostname if not urlsplit.port 
                                  else "%s:%i" % (urlsplit.hostname, urlsplit.port),
                urlsplit[2],
                urlsplit[3],
                urlsplit[4]])
            self.set_credentials(urlsplit.username, urlsplit.password)
        else:
            self.url = urlparse.urlunsplit(urlsplit)
    
    def set_credentials(self, username, password):
        self.additional_headers['authorization'] = "Basic: %s" % base64.b64encode("%s:%s" % (username, password))
    
    def list_items(self):
        resp, data = self.http.request(self.url, headers=self.additional_headers)
        if not 200 <= resp.status <= 299:
            raise RepositoryException("Could not load version list: HTTP error %i (%s)" % (resp.status, resp.reason))
        link_extractor = LinkExtractor()
        link_extractor.feed(data)
        return self._filter_items(link_extractor.links)
    
    def load_item(self, name):
        resp, data = self.http.request(self._url_from_name(name), headers=self.additional_headers)
        if not 200 <= resp.status <= 299:
            raise RepositoryException("Could not load item: HTTP error %i (%s)" % (resp.status, resp.reason))
        return data
    
    def store_item(self, name, data):
        resp, data = self.http.request(self._url_from_name(name), method="PUT", body=data, headers=self.additional_headers)
        if not 200 <= resp.status <= 299:
            raise RepositoryException("Could not store item: HTTP error %i (%s)" % (resp.status, resp.reason))
    
    def _url_from_name(self, name):
        return urlparse.urljoin(self.url, urllib.quote(name))


class McHttpRepositoryShortcut(McHttpRepository):
    locations = dict(
        hpi="http://www.hpi.uni-potsdam.de/hirschfeld/squeaksource/%s/",
        lukas="http://source.lukas-renggli.ch/%s/",
        squeak="http://source.squeak.org/%s/",
        squeakfoundation="http://source.squeakfoundation.org/%s/",
        ss="http://www.squeaksource.com/%s/",
        wiresong="http://source.wiresong.ca/%s/",
    )
    
    def __init__(self, url):
        base, identifier = url.split(":", 1)
        if base not in self.locations:
            raise RepositoryException("Unknown shortcut: %s", base)
        credentials, _, position = identifier.rpartition("@")
        
        super(McHttpRepositoryShortcut, self).__init__(self.locations[base] % position)
        
        if credentials:
            self.set_credentials(*credentials.split(":", 1))
