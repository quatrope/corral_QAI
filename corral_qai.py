#!/usr/bin/env python
# -*- coding: utf-8 -*-

#~ This code is part of Corral (https://github.com/toros-astro/corral)
#~ Author Juan B Cabral
#~ License: BSD 3

import os
import requests
import datetime
import random
import time
import tempfile
import json
import atexit
import shutil
import uuid
import codecs
import hashlib
import sys
import abc

import peewee as pw

import six

import sh

import dateutil.parser

import xmltodict

import bs4

import settings


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))

DATA_PATH = os.path.join(PATH, "data")

DB_PATH = os.path.join(DATA_PATH, "corral_qai.db")


# =============================================================================
# CONF
# =============================================================================

flake8 = sh.flake8.bake(statistics=True, count=True, exit_zero=True)


# =============================================================================
# DATABASE
# =============================================================================

db = pw.SqliteDatabase(DB_PATH)

class TimeStamps(pw.Model):
    class Meta:
        database = db

    timestamp = pw.DateTimeField(null=True)
    source = pw.CharField(max_length=255)


class PythonFile(pw.Model):
    class Meta:
        database = db

    timestamp = pw.DateTimeField(default=datetime.datetime.now)
    response = pw.TextField()

    source = pw.CharField(max_length=255)
    source_id = pw.CharField(max_length=255)
    description = pw.TextField()

    file_name = pw.TextField()
    file_sha512 = pw.CharField(max_length=200, unique=True)
    file_raw_url = pw.TextField()
    file_size = pw.IntegerField()

    file_content = pw.TextField()

    flake8_output = pw.TextField()
    flake8_errors = pw.IntegerField()

db.connect()
db.create_tables([PythonFile, TimeStamps], safe=True)

# =============================================================================
# BASE CLASS
# =============================================================================

@six.add_metaclass(abc.ABCMeta)
class Extractor(object):

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="corral_qai")
        atexit.register(shutil.rmtree, self.temp_dir)

    def random_sleep(self):
        rnd = random.randint(1, 2) + random.random()
        self.log(u"Sleeping '{}'...".format(rnd))
        time.sleep(rnd)

    def log(self, msg):
        source = self.get_source()
        print("[{}] {}".format(source, msg))

    def get_since(self):
        source = self.get_source()
        ts = TimeStamps.create_or_get(id=1, source=source)[0]
        return ts.timestamp

    def store_timestamp(self):
        source = self.get_source()
        ts = TimeStamps.create_or_get(id=1, source=source)[0]
        ts.timestamp = datetime.datetime.now()
        ts.save()

    def write_temppyfile(self, content):
        self.log(u"Writing temp file...")
        basename = "cqai_code{}.py".format(uuid.uuid4())
        path = os.path.join(self.temp_dir, basename)
        with codecs.open(path, "w", encoding="utf8") as fp:
            fp.write(content)
        return path

    def run_flake8(self, path):
        self.log(u"Running flake8...")
        run = flake8(path)
        return run.stdout.strip(), int(run.stderr.strip() or "0")

    def save(self, **data):
        self.log(u"Generating Hash")
        file_sha512 = hashlib.sha512(
            data["file_content"].encode("utf8")
        ).hexdigest()
        file_exists = PythonFile.select().where(
            PythonFile.file_sha512==file_sha512).exists()

        if not file_exists:
            source = self.get_source()
            path = self.write_temppyfile(data["file_content"])
            flake8_output, flake8_errors = self.run_flake8(path)
            self.log("Storing !!!")
            PythonFile.create(
                flake8_output=flake8_output, flake8_errors=flake8_errors,
                source=source, file_sha512=file_sha512, **data)
        else:
            self.log("File Exists !!!")
            self.on_file_exist(
                file_sha512=file_sha512, source=self.get_source(), **data)

    def on_file_exist(self, **data):
        pass

    def setup(self):
        pass

    @abc.abstractmethod
    def get_source(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def query(self):
        raise NotImplementedError()

    def run(self):
        self.setup()
        since = self.get_since()
        self.store_timestamp()
        for file_data in self.query(since):
            self.save(**file_data)


# =============================================================================
# GISTS
# =============================================================================

class GistExtractor(Extractor):

    def get_source(self):
        return "gist"

    def requests_get(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            msg = response.json().get(
                "message", u"Error: " + unicode(response.reason))
            self.log(msg)
            sys.exit(1)
        return response

    def process_gist_page(self, response):
        gists = response.json()
        for gist in gists:
            gist_dict = {
                u'source_id': gist["id"],
                u'response': json.dumps(gist),
                u'description': gist.get("description") or ""}

            for file_key, file_data in gist.get("files", {}).items():
                file_type = file_data["type"]
                if file_type in (u"application/x-python",):
                    self.log(u"Retrieving '{}'...".format(file_key))
                    file_content = self.requests_get(file_data["raw_url"]).text

                    file_dict = {
                        "file_name": file_data["filename"],
                        "file_raw_url": file_data["raw_url"],
                        "file_size": file_data["size"],
                        "file_content": file_content,
                    }
                    file_dict.update(gist_dict)
                    yield file_dict

    def query(self, since):
        url_tpl = "https://api.github.com/gists/public?&page={}"
        #~ if since:
            #~ url_tpl += "since=" + since

        counter = 0
        while counter < 200:
            page = counter
            self.log(u"Retrieving '{}/200'...".format(page+1))
            url = url_tpl.format(page+1)
            response = self.requests_get(url)
            for file_data in self.process_gist_page(response):
                yield file_data
            self.random_sleep()
            counter += 1


# =============================================================================
# PASTEBIN
# =============================================================================

class PastebinExtractor(Extractor):

    def get_source(self):
        return "pastebin"

    def setup(self):
        self.api_dev_key = settings.PASTEBIN["api_dev_key"]

    def query(self, since):
        for pd in self.trends(since):
            yield pd
        self.random_sleep()
        for pd in self.archive(since):
            yield pd

    def archive(self, since):
        def a_not_archive(tag):
            return (
                tag.name.lower() == "a" and not
                tag.attrs["href"].startswith("/archive/python"))

        request = requests.get("http://pastebin.com/archive/python")
        self.random_sleep()
        html = request.text

        soup = bs4.BeautifulSoup(html, "html.parser")
        maintable = soup.find("table", class_="maintable")
        for anchor in maintable.findAll(a_not_archive):
            paste_key = anchor.attrs["href"][1:]
            paste_raw_url = "http://pastebin.com/raw/{}".format(paste_key)

            self.log("Retrieving '{}'...".format(paste_key))
            paste_content = requests.get(paste_raw_url).text
            paste_dict = {
                    u'source_id': paste_key,
                    u'response': html,
                    u'description': anchor.text,
                    u'file_name': "pastebin_{}.py".format(paste_key),
                    u'file_size': len(paste_content),
                    u'file_raw_url': paste_raw_url,
                    u'file_content': paste_content}
            yield paste_dict
            self.random_sleep()

    def trends(self, since):
        data = {"api_option": "trends", "api_dev_key": self.api_dev_key}
        url = "http://pastebin.com/api/api_post.php"

        request = requests.post(url, data=data)
        xml = u"<pastes>{}</pastes>".format(request.text)

        pastes = xmltodict.parse(xml)
        for paste in pastes["pastes"]["paste"]:
            is_public = int(paste["paste_private"]) < 2
            if paste["paste_format_short"] == "python" and is_public:
                paste_key = paste["paste_key"]
                paste_raw_url = "http://pastebin.com/raw/{}".format(paste_key)

                self.log("Retrieving '{}'...".format(paste_key))
                paste_content = requests.get(paste_raw_url).text
                paste_dict = {
                    u'source_id': paste_key,
                    u'response': json.dumps(paste),
                    u'description': paste.get("paste_title") or "",
                    u'file_name': "pastebin_{}.py".format(paste_key),
                    u'file_size': int(paste["paste_size"]),
                    u'file_raw_url': paste_raw_url,
                    u'file_content': paste_content}
                yield paste_dict


class ActivestateExtractor(Extractor):

    def get_source(self):
        return "ActiveState Recipes"

    def get_title_url(self, rdiv):
        recipe_title_span = rdiv.find("span", class_="recipe-title")
        title = recipe_title_span.a.text or ""
        base_url = recipe_title_span.a.attrs["href"]
        if "?" in base_url:
            base_url = base_url.split("?", 1)[0]
        raw_url = "http://code.activestate.com" + base_url + "download/1/"
        return title, raw_url

    def on_file_exist(self, **data):
        import sys;sys.exit(0)

    def query(self, since):
        url_tpl = "http://code.activestate.com/recipes/langs/python/?page={}"
        for idx in [1]:
            url = url_tpl.format(idx)
            response = requests.get(url)
            html = response.text
            soup = bs4.BeautifulSoup(html, "html.parser")
            ul = soup.find("ul", class_="recipes")
            self.random_sleep()
            for recipe_div in ul.find_all("div", class_="recipe-summary-compact"):
                as_id = recipe_div.attrs["id"]
                as_title, as_raw_url = self.get_title_url(recipe_div)
                as_content = requests.get(as_raw_url).text
                as_dict = {
                    u'source_id': as_id,
                    u'response': html,
                    u'description': as_title,
                    u'file_name': "as_{}.py".format(as_id),
                    u'file_size': len(as_content),
                    u'file_raw_url': as_raw_url,
                    u'file_content': as_content}
                yield as_dict
                self.random_sleep()
            print ">>>>>>>>>>>>>>>> END PAGE", idx


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python corral_qai {gist|pastebin|activestate}")
        sys.exit(1)
    cls_name = "{}Extractor".format(sys.argv[-1].title())
    cls = locals().get(cls_name)
    if cls is None or not issubclass(cls, Extractor):
        raise ValueError("'{}' is not a valid extractor".format(cls_name))
    print("[Starting '{}']".format(cls_name))
    cls().run()

