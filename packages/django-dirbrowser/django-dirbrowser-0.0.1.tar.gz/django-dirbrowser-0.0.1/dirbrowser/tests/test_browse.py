# -*- coding: utf-8 -*-
"""
    Tests for django-dirbrowser
"""
import os
import mimetypes
import time
from datetime import datetime
from django.test import TestCase
from django.utils.http import http_date

from urls import BROWSE_DIR


class DirBrowserTest(TestCase):
    """
        dirbrowser test case
    """
    urls = 'dirbrowser.tests.urls'
    basedir = '/browse'

    def test_browse_redirect_slash(self):
        resp = self.client.get(self.basedir)
        self.assertEqual(resp.status_code, 301)

    def test_browse_dir(self):
        resp = self.client.get(self.basedir + "/")
        self.assertEqual(resp.status_code, 200)
        if self.basedir == '/browse':
            self.assertEqual(resp.context['extra_value'], "value")
        else:
            self.assertFalse('extra_value' in resp.context)

    def test_browse_subdir(self):
        resp = self.client.get(self.basedir + "/directory/")
        self.assertEqual(resp.status_code, 200)
        if self.basedir == '/browse':
            self.assertEqual(resp.context['extra_value'], "value")
        else:
            self.assertFalse('extra_value' in resp.context)

    def test_browse_non_Existent(self):
        resp = self.client.get(self.basedir + "/aaaa")
        self.assertEqual(resp.status_code, 404)

    def test_browse_get_file(self):
        resp = self.client.get(self.basedir + "/random_data")
        self.assertEqual(resp.status_code, 200)

    def test_browse_get_gzipped(self):
        resp = self.client.get(self.basedir + "/random_data.gz")
        self.assertEqual(resp.status_code, 200)

    def test_browse_get_text(self):
        resp = self.client.get(self.basedir + "/directory/some_text_file.txt")
        self.assertEqual(resp.status_code, 200)


class DirBrowser2Test(DirBrowserTest):
    """
        dirbrowser test case
    """
    basedir = '/browse2'


class DownloadTest(TestCase):
    """
        dirbrowser test case
    """
    urls = 'dirbrowser.tests.urls'

    def test_download_dir(self):
        resp = self.client.get("/download/")
        self.assertEqual(resp.status_code, 404)

    def test_download_redirect_slash(self):
        resp = self.client.get("/download")
        self.assertEqual(resp.status_code, 301)

    def test_download_file(self):
        resp = self.client.get("/download/random_data")
        self.assertEqual(resp.status_code, 200)

    def test_download_gzipped(self):
        resp = self.client.get("/download/random_data.gz")
        self.assertEqual(resp.status_code, 200)


FILES = []
DIRS = []


def load_files():
    global FILES, DIRS
    length = len(BROWSE_DIR)

    for (dirpath, dirnames, filenames) in os.walk(BROWSE_DIR):
        for filename in filenames:
            url = dirpath[length:] + '/' + filename
            fullpath = os.path.join(dirpath, filename)
            mimetype, encoding = mimetypes.guess_type(fullpath)
            mimetype = mimetype or 'application/octet-stream'
            size = os.path.getsize(fullpath)
            mtime = datetime.fromtimestamp(os.path.getmtime(fullpath))
            FILES.append((url, (mimetype, encoding), size, mtime))

        dirname = dirpath[length:] + '/'
        DIRS.append((dirname, filenames + dirnames))

load_files()


class TestDataTest(TestCase):
    """
        dirbrowser test case
    """
    urls = 'dirbrowser.tests.urls'

    def test_files_status(self):
        for testfile in FILES:
            url = "/browse/" + testfile[0]
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

    def test_files_mimetype(self):
        for testfile in FILES:
            url = "/browse/" + testfile[0]
            resp = self.client.get(url)
            mimetype, encoding = testfile[1]
            self.assertEqual(resp['Content-Type'], mimetype)
            if encoding:
                self.assertEqual(resp['Content-Encoding'], encoding)
            else:
                self.assertFalse('Content-Encoding' in resp)

    def test_files_size(self):
        for testfile in FILES:
            url = "/browse/" + testfile[0]
            resp = self.client.get(url)
            size = testfile[2]
            self.assertEqual(int(resp["Content-Length"]), size)

    def test_files_time(self):
        for testfile in FILES:
            url = "/browse/" + testfile[0]
            resp = self.client.get(url)
            mtime = http_date(time.mktime(testfile[3].timetuple()))
            self.assertEqual(resp["Last-Modified"], mtime)


class TestDirContent(TestCase):
    """
        dirbrowser test case
    """
    urls = 'dirbrowser.tests.urls'

    def test_dir_content(self):
        for dirname, files in DIRS:
            url = "/browse/" + dirname
            resp = self.client.get(url)
            for filename in files:
                self.assertContains(resp, filename)


class SecurityTest(TestCase):
    """
        dirbrowser test case
    """
    urls = 'dirbrowser.tests.urls'

    def test_security1(self):
        resp = self.client.get("/browse/../")
        self.assertEqual(resp.status_code, 200)

    def test_security2(self):
        resp = self.client.get("/browse/aaa/../")
        self.assertEqual(resp.status_code, 200)

    def test_security3(self):
        resp = self.client.get("/browse/aaa/../bbb/")
        self.assertEqual(resp.status_code, 404)

    def test_security4(self):
        resp = self.client.get("/browse/aaa/../bbb/../")
        self.assertEqual(resp.status_code, 200)

    def test_security5(self):
        resp = self.client.get("/browse/aaa\\..\\bbb/")
        self.assertEqual(resp.status_code, 302)


class ModifiedHeaderTest(TestCase):

    urls = 'dirbrowser.tests.urls'
    filename = "/browse/random_data"

    def test_modified_header(self):

        resp = self.client.get(self.filename)
        self.assertEqual(resp.status_code, 200)

        date = resp["Last-Modified"]
        resp = self.client.get(self.filename, HTTP_IF_MODIFIED_SINCE=date)
        self.assertEqual(resp.status_code, 304)

    def test_modified_header_none(self):

        resp = self.client.get(self.filename, HTTP_IF_MODIFIED_SINCE=None)
        self.assertEqual(resp.status_code, 200)
