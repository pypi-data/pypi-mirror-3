import pkg_resources
import os
import shutil
import weakref
import urllib
import urllib2
import re
import zipfile
import tempfile
from urlparse import urlparse

index_pkg_link_re = re.compile(
    r'<a href="(?P<link>[^"\']+)">(?P<name>\S+)</a>')


class MyEnvironment(pkg_resources.Environment):
    def obtain(self, requirement, installer):
        self.parent.obtain(requirement, installer)


class EggFinder(object):
    def __init__(self, packer):
        self.packer = packer
        self._index_packages = None

        self.env = MyEnvironment(
            search_path=[], platform=self.packer.platform,
            python=self.packer.python)

        self.env.parent = weakref.proxy(self)
        self.ws = pkg_resources.WorkingSet(entries=[])

        self.obtain_recurse_lock = False

    def obtain(self, requirement, installer):
        pass

    def myobtain(self, requirement, installer):
        if self.obtain_recurse_lock:
            return None
        print "Looking for %s" % requirement
        self.obtain_recurse_lock = True
        try:
            if requirement.key in self.index_packages:
                for name, link in self.read_links(
                        self.index_packages[requirement.key]['link']):
                    d = pkg_resources.Distribution.from_location(link, name)
                    if self.env.can_add(d):
                        self.env.add(d)
                        print "Found %s" % (name)
                    else:
                        print "Ignoring %s" % (name)
            return self.env.best_match(requirement, self.ws)
        finally:
            self.obtain_recurse_lock = False
        return None

    def read_links(self, url):

        links = []

        print "Reading %s" % url
        content = urllib2.urlopen(url).read()

        for m in index_pkg_link_re.finditer(content):
            name = m.group('name')
            link = m.group('link')
            if not link.startswith('http'):
                p = urlparse(url)
                if link.startswith('/'):
                    link = '%s://%s%s' % (
                        p.scheme, p.netloc, link)
                else:
                    link = '%s://%s%s/%s' % (
                        p.scheme, p.netloc, os.path.dirname(p.path), link)
            links.append((name, link))

        return links

    @property
    def index_packages(self):
        if self._index_packages is None:
            self._index_packages = dict(
                (name.lower(), dict(name=name, link=link))
                for name, link in self.read_links(self.packer.index))
        return self._index_packages

    def find(self, req):
        d = self.env.best_match(req, self.ws)
        if not d:
            d = self.myobtain(req, self.ws)
        if d:
            return d.location


class EggsPacker(object):
    def __init__(self, index=None, basket=None, python=None, platform=None,
            unzip=[]):
        self.index = index
        self.basket = basket
        self.python = python
        self.platform = platform

        self.downloaddir = tempfile.mkdtemp()

        self.unzip = set([key.lower() for key in unzip])

        self.env = pkg_resources.Environment(
            search_path=self.basket,
            platform=self.platform,
            python=self.python)
        self.env.scan([self.basket])
        self.ws = pkg_resources.WorkingSet([self.basket])

        self.finder = EggFinder(weakref.proxy(self))

    def obtain(self, requirement):
        print "Will try to obtain %s" % requirement

        url = self.finder.find(requirement)
        if url:
            parsed_url = urlparse(url)
            fname = os.path.join(
                self.downloaddir,
                os.path.basename(parsed_url.path))
            print "Downloading %s" % url
            urllib.urlretrieve(url, fname)
            self.add(fname)
            os.remove(fname)

    def best_match(self, requirement):
        d = self.env.best_match(requirement, self.ws)
        if not d:
            self.obtain(requirement)
            d = self.env.best_match(requirement, self.ws)
        return d

    def need_unzip(self, dist):
        if 'all' in self.unzip or \
                'auto' in self.unzip and not dist.has_metadata('zip-safe') or \
                dist.key in self.unzip:
            return True
        return False

    def add(self, filename):
        dist = pkg_resources.Distribution.from_filename(
            filename, metadata=pkg_resources.EggMetadata(
                         pkg_resources.get_importer(filename)))
        tgt_eggname = os.path.join(self.basket, os.path.basename(dist.location))
        if self.need_unzip(dist):
            print "Unzipping %s" % dist.egg_name()
            if os.path.exists(tgt_eggname):
                if os.path.isdir(tgt_eggname):
                    shutil.rmtree(tgt_eggname)
                else:
                    os.remove(tgt_eggname)
            os.mkdir(tgt_eggname)
            arch = zipfile.ZipFile(dist.location)
            for name in arch.namelist():
                if name.endswith('/'):
                    continue
                fname = os.path.join(tgt_eggname, name)
                dirname = os.path.dirname(fname)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                f = open(fname, 'wb')
                try:
                    f.write(arch.read(name))
                finally:
                    f.close()
        else:
            shutil.copyfile(dist.location, tgt_eggname)

        self.env.scan([self.basket])

    def pack(self, egg):
        if isinstance(egg, basestring) and os.path.exists(egg):
            egg_dist = pkg_resources.Distribution.from_filename(
                    egg, metadata=pkg_resources.EggMetadata(
                         pkg_resources.get_importer(egg)))
            if egg_dist.py_version != self.python:
                raise ValueError('Wrong python version')
            if egg_dist.platform not in (None, self.platform):
                raise ValueError('Wrong platform')
            self.add(egg_dist.location)
            req = egg_dist.as_requirement()

        elif isinstance(egg, basestring):
            req = pkg_resources.Requirement.parse(egg)
        else:
            req = egg

        egg_dist = self.best_match(req)

        if egg_dist is None:
            raise RuntimeError("Could not pack %s" % req)

        self.ws.add(egg_dist)

        print "Checking dependencies for %s" % egg_dist.as_requirement()

        for req in egg_dist.requires():
            if req.key in ('setuptools'):
                pass
            if not self.ws.find(req):
                self.pack(req)
