import os
import sys
import glob
import json
import time
import socket
import tempfile
import unittest

if sys.version_info[0] < 3:
    import robotparser
    from StringIO import StringIO
else:
    from urllib import robotparser
    from io import StringIO

import mock
import httplib2
import scrapelib

HTTPBIN = 'http://httpbin.org/'


class HeaderTest(unittest.TestCase):
    def test_keys(self):
        h = scrapelib.Headers()
        h['A'] = '1'

        self.assertEqual(h['A'], '1')

        self.assertEqual(h.getallmatchingheaders('A'), ["A: 1"])
        self.assertEqual(h.getallmatchingheaders('b'), [])
        self.assertEqual(h.getheaders('A'), ['1'])
        self.assertEqual(h.getheaders('b'), [])

        # should be case-insensitive
        self.assertEqual(h['a'], '1')
        h['a'] = '2'
        self.assertEqual(h['A'], '2')

        self.assertTrue('a' in h)
        self.assertTrue('A' in h)

        del h['A']
        self.assertTrue('a' not in h)
        self.assertTrue('A' not in h)

    def test_equality(self):
        h1 = scrapelib.Headers()
        h1['Accept-Encoding'] = '*'

        h2 = scrapelib.Headers()
        self.assertNotEqual(h1, h2)

        h2['accept-encoding'] = 'not'
        self.assertNotEqual(h1, h2)

        h2['accept-encoding'] = '*'
        self.assertEqual(h1, h2)


class ScraperTest(unittest.TestCase):

    def _setup_cache(self):
        self.cache_dir = tempfile.mkdtemp()
        self.error_dir = tempfile.mkdtemp()
        self.s = scrapelib.Scraper(requests_per_minute=0,
                                   error_dir=self.error_dir,
                                   cache_dir=self.cache_dir,
                                   use_cache_first=True)


    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()
        self.error_dir = tempfile.mkdtemp()
        self.s = scrapelib.Scraper(requests_per_minute=0,
                                   error_dir=self.error_dir,
                                   follow_robots=False
                                  )

    def tearDown(self):
        if hasattr(self, 'cache_dir'):
            for path in glob.iglob(os.path.join(self.cache_dir, "*")):
                os.remove(path)
            os.rmdir(self.cache_dir)
        for path in glob.iglob(os.path.join(self.error_dir, "*")):
            os.remove(path)
        os.rmdir(self.error_dir)

    def test_constructor(self):
        # timeout=0 means None
        s = scrapelib.Scraper(timeout=0)
        assert s.timeout is None

    def test_get(self):
        resp = self.s.urlopen(HTTPBIN + 'get?woo=woo')
        self.assertEqual(resp.response.code, 200)
        self.assertEqual(json.loads(resp)['args']['woo'], 'woo')

    def test_post(self):
        resp = self.s.urlopen(HTTPBIN + 'post', 'POST', 'woo=woo')
        self.assertEqual(resp.response.code, 200)
        resp_json = json.loads(resp)
        self.assertEqual(resp_json['form']['woo'], 'woo')
        self.assertEqual(resp_json['headers']['Content-Type'],
                         'application/x-www-form-urlencoded')

    def test_bytes(self):
        raw_bytes = b'\xb5\xb5'
        mock_do_request = mock.Mock(return_value=(
            scrapelib.Response('', '', code=200), raw_bytes))

        # check that sleep is called
        with mock.patch.object(self.s, '_do_request', mock_do_request):
            resp = self.s.urlopen('http://dummy/bin/')
            self.assertEqual(resp.response.code, 200)
            self.assertEqual(resp.bytes, raw_bytes)

    def test_request_throttling(self):
        s = scrapelib.Scraper(requests_per_minute=30, follow_robots=False,
                              accept_cookies=False)
        self.assertEqual(s.requests_per_minute, 30)

        # mock to quickly return a dummy response
        mock_do_request = mock.Mock(return_value=(
            scrapelib.Response('', '', code=200), 'ok'))
        mock_sleep = mock.Mock()

        # check that sleep is called
        with mock.patch('time.sleep', mock_sleep):
            with mock.patch.object(s, '_do_request', mock_do_request):
                s.urlopen('http://dummy/')
                s.urlopen('http://dummy/')
                s.urlopen('http://dummy/')
                self.assertTrue(mock_sleep.call_count == 2)
                # should have slept for ~2 seconds
                self.assertTrue(1.8 <= mock_sleep.call_args[0][0] <= 2.2)
                self.assertTrue(mock_do_request.call_count == 3)

        # unthrottled, should be able to fit in lots of calls
        s.requests_per_minute = 0
        mock_do_request.reset_mock()
        mock_sleep.reset_mock()

        with mock.patch('time.sleep', mock_sleep):
            with mock.patch.object(s, '_do_request', mock_do_request):
                s.urlopen('http://dummy/')
                s.urlopen('http://dummy/')
                s.urlopen('http://dummy/')
                self.assertTrue(mock_sleep.call_count == 0)
                self.assertTrue(mock_do_request.call_count == 3)

    def test_user_agent(self):
        resp = self.s.urlopen(HTTPBIN + 'user-agent')
        ua = json.loads(resp)['user-agent']
        self.assertEqual(ua, scrapelib._user_agent)

        self.s.user_agent = 'a different agent'
        resp = self.s.urlopen(HTTPBIN + 'user-agent')
        ua = json.loads(resp)['user-agent']
        self.assertEqual(ua, 'a different agent')

    def test_default_to_http(self):

        def do_request(url, *args, **kwargs):
            return scrapelib.Response(url, url, code=200), ''
        mock_do_request = mock.Mock(wraps=do_request)

        with mock.patch.object(self.s, '_do_request', mock_do_request):
            self.assertEqual('http://dummy/',
                             self.s.urlopen("dummy/").response.url)

    def test_follow_robots(self):
        self.s.follow_robots = True

        def do_request(url, *args, **kwargs):
            return scrapelib.Response(url, url, code=200), ''

        with mock.patch.object(self.s, '_do_request', do_request):

            # set a fake robots.txt for http://dummy
            parser = robotparser.RobotFileParser()
            parser.parse(['User-agent: *', 'Disallow: /private/', 'Allow: /'])
            self.s._robot_parsers['http://dummy/robots.txt'] = parser

            # anything behind private fails
            self.assertRaises(scrapelib.RobotExclusionError, self.s.urlopen,
                              "http://dummy/private/secret.html")
            # but others work
            self.assertEqual(200,
                             self.s.urlopen("http://dummy/").response.code)

            # turn off follow_robots, everything works
            self.s.follow_robots = False
            self.assertEqual(200,
             self.s.urlopen("http://dummy/private/secret.html").response.code)

    def test_error_context(self):
        def do_request(url, *args, **kwargs):
            return scrapelib.Response(url, url, code=200), ''
        mock_do_request = mock.Mock(wraps=do_request)

        with mock.patch.object(self.s, '_do_request', mock_do_request):
            def raises():
                with self.s.urlopen("http://dummy/"):
                    raise Exception('test')

            self.assertRaises(Exception, raises)
        self.assertTrue(os.path.isfile(os.path.join(
            self.error_dir, "http:,,dummy,")))

    def test_404(self):
        self.assertRaises(scrapelib.HTTPError, self.s.urlopen,
                          HTTPBIN + 'status/404')

        self.s.raise_errors = False
        resp = self.s.urlopen(HTTPBIN + 'status/404')
        self.assertEqual(404, resp.response.code)

    def test_500(self):
        self.assertRaises(scrapelib.HTTPError, self.s.urlopen,
                          HTTPBIN + 'status/500')

        self.s.raise_errors = False
        resp = self.s.urlopen(HTTPBIN + 'status/500')
        self.assertEqual(resp.response.code, 500)

    def test_follow_redirect(self):
        redirect_url = HTTPBIN + 'redirect/1'
        final_url = HTTPBIN + 'get'

        resp = self.s.urlopen(redirect_url)
        self.assertEqual(final_url, resp.response.url)
        self.assertEqual(redirect_url, resp.response.requested_url)
        self.assertEqual(200, resp.response.code)

        self.s.follow_redirects = False
        resp = self.s.urlopen(redirect_url)
        self.assertEqual(redirect_url, resp.response.url)
        self.assertEqual(redirect_url, resp.response.requested_url)
        self.assertEqual(302, resp.response.code)

    def test_post_redirect(self):
        orig_request = self.s._do_request
        def do_request(url, *args, **kwargs):
            if 'dummy' in url:
                return scrapelib.Response(url, url, code=301,
                  headers={'location':HTTPBIN + 'status/200'}), ''
            else:
                return orig_request(url, *args, **kwargs)
        mock_do_request = mock.Mock(wraps=do_request)

        with mock.patch.object(self.s, '_do_request', mock_do_request):
            resp = self.s.urlopen('http://dummy/')
            assert resp.response.code == 200
            assert resp.response.url == HTTPBIN + 'status/200'
            assert resp.response.requested_url == 'http://dummy/'
        assert mock_do_request.call_count == 2

    def test_caching(self):
        self._setup_cache()

        resp = self.s.urlopen(HTTPBIN + 'status/200')
        self.assertFalse(resp.response.fromcache)
        resp = self.s.urlopen(HTTPBIN + 'status/200')
        self.assertTrue(resp.response.fromcache)

        self.s.use_cache_first = False
        resp = self.s.urlopen(HTTPBIN + 'status/200')
        self.assertFalse(resp.response.fromcache)

    def test_urlretrieve(self):
        # assume urlopen works fine
        content = scrapelib.ResultStr(self.s,
                                      scrapelib.Response('', '', code=200),
                                      'in your file')
        fake_urlopen = mock.Mock(return_value=content)

        with mock.patch.object(self.s, 'urlopen', fake_urlopen):
            fname, resp = self.s.urlretrieve("http://dummy/")
            with open(fname) as f:
                self.assertEqual(f.read(), 'in your file')
                self.assertEqual(200, resp.code)
            os.remove(fname)

            (fh, set_fname) = tempfile.mkstemp()
            fname, resp = self.s.urlretrieve("http://dummy/",
                                             set_fname)
            self.assertEqual(fname, set_fname)
            with open(set_fname) as f:
                self.assertEqual(f.read(), 'in your file')
                self.assertEqual(200, resp.code)
            os.remove(set_fname)

    # TODO: on these retry tests it'd be nice to ensure that it tries
    # 3 times for 500 and once for 404

    def test_retry(self):
        s = scrapelib.Scraper(retry_attempts=3, retry_wait_seconds=0.1)

        # On the first call return a 500, then a 200
        side_effect = [
            (httplib2.Response({'status': 500}), 'failure!'),
            (httplib2.Response({'status': 200}), 'success!')
        ]

        mock_request = mock.Mock(side_effect=side_effect)

        with mock.patch.object(httplib2.Http, 'request', mock_request):
            resp, content = s._do_request('http://dummy/', 'GET', None, {})
        self.assertEqual(mock_request.call_count, 2)

        # 500 always
        resp, content = s._do_request(HTTPBIN + 'status/500',
                                      'GET', None, {})
        self.assertEqual(resp.code, 500)

    def test_retry_404(self):
        s = scrapelib.Scraper(retry_attempts=3, retry_wait_seconds=0.1)

        # On the first call return a 404, then a 200
        side_effect = [
            (httplib2.Response({'status': 404}), 'failure!'),
            (httplib2.Response({'status': 200}), 'success!')
        ]

        mock_request = mock.Mock(side_effect=side_effect)

        with mock.patch.object(httplib2.Http, 'request', mock_request):
            resp, content = s._do_request('http://localhost:5000/',
                                          'GET', None, {}, retry_on_404=True)
        self.assertEqual(mock_request.call_count, 2)

        # 404
        resp, content = s._do_request(HTTPBIN + 'status/404',
                                      'GET', None, {})
        self.assertEqual(resp.code, 404)

    def test_socket_retry(self):
        count = []

        # On the first call raise socket.timeout
        # On subsequent calls pass through to httplib2.Http.request
        def side_effect(*args, **kwargs):
            if count:
                return httplib2.Response({'status': 200}), 'success!'
            count.append(1)
            raise socket.timeout('timed out :(')

        mock_request = mock.Mock(side_effect=side_effect)

        with mock.patch.object(httplib2.Http, 'request', mock_request):
            s = scrapelib.Scraper(retry_attempts=0, retry_wait_seconds=0.001, 
                                  follow_robots=False)
            # try only once, get the error
            self.assertRaises(socket.timeout, self.s.urlopen, "http://dummy/")
            self.assertEqual(mock_request.call_count, 1)

        mock_request.reset_mock()
        count = []
        with mock.patch.object(httplib2.Http, 'request', mock_request):
            s = scrapelib.Scraper(retry_attempts=2, retry_wait_seconds=0.001,
                                  follow_robots=False)
            resp = s.urlopen("http://dummy/")
            # get the result, take two tries
            self.assertEqual(resp, "success!")
            self.assertEqual(mock_request.call_count, 2)

    def test_httplib2_nasty_workaround(self):
        """ test workaround for httplib2 breakage """
        count = []

        # On the first call raise socket.timeout
        # On subsequent calls pass through to httplib2.Http.request
        def side_effect(*args, **kwargs):
            if count:
                return httplib2.Response({'status': 200}), 'success!'
            count.append(1)
            raise AttributeError("'NoneType' object has no attribute "
                                 "'makefile'")

        mock_request = mock.Mock(side_effect=side_effect)

        with mock.patch.object(httplib2.Http, 'request', mock_request):
            s = scrapelib.Scraper(retry_attempts=0, retry_wait_seconds=0.001, 
                                  follow_robots=False)
            # try only once, get the error
            self.assertRaises(AttributeError, self.s.urlopen, "http://dummy/")
            self.assertEqual(mock_request.call_count, 1)

        mock_request.reset_mock()
        count = []
        with mock.patch.object(httplib2.Http, 'request', mock_request):
            s = scrapelib.Scraper(retry_attempts=2, retry_wait_seconds=0.001,
                                  follow_robots=False)
            resp = s.urlopen("http://dummy/")
            # get the result, take two tries
            self.assertEqual(resp, "success!")
            self.assertEqual(mock_request.call_count, 2)


    def test_disable_compression(self):
        s = scrapelib.Scraper(disable_compression=True)

        headers = s._make_headers("http://google.com")
        self.assertEqual(headers['accept-encoding'], 'text/*')

        # A supplied Accept-Encoding headers overrides the
        # disable_compression option
        s.headers['accept-encoding'] = '*'
        headers = s._make_headers('http://google.com')
        self.assertEqual(headers['accept-encoding'], '*')

    def test_callable_headers(self):
        s = scrapelib.Scraper(headers=lambda url: {'URL': url})

        headers = s._make_headers('http://google.com')
        self.assertEqual(headers['url'], 'http://google.com')

        # Make sure it gets called freshly each time
        headers = s._make_headers('http://example.com')
        self.assertEqual(headers['url'], 'http://example.com')

    def test_ftp_uses_urllib2(self):
        urlopen = mock.Mock(return_value=StringIO("ftp success!"))

        with mock.patch('scrapelib.urllib_urlopen', urlopen):
            r = self.s.urlopen('ftp://dummy/')
            assert r == "ftp success!"

    def test_ftp_retries(self):
        count = []

        # On the first call raise URLError, then work
        def side_effect(*args, **kwargs):
            if count:
                return StringIO("ftp success!")
            count.append(1)
            raise scrapelib.urllib_URLError('550: ftp failure!')

        mock_urlopen = mock.Mock(side_effect=side_effect)

        # retry on, retry_on_404 on (will retry due to 550 code)
        with mock.patch('scrapelib.urllib_urlopen', mock_urlopen):
            s = scrapelib.Scraper(retry_attempts=2, retry_wait_seconds=0.001,
                                  follow_robots=False)
            r = s.urlopen('ftp://dummy/', retry_on_404=True)
            assert r == "ftp success!"
        self.assertEquals(mock_urlopen.call_count, 2)

        # retry off, retry_on_404 on (shouldn't matter)
        count = []
        mock_urlopen.reset_mock()
        with mock.patch('scrapelib.urllib_urlopen', mock_urlopen):
            s = scrapelib.Scraper(retry_attempts=0, retry_wait_seconds=0.001,
                                  follow_robots=False)
            self.assertRaises(scrapelib.urllib_URLError,
                              s.urlopen, 'ftp://dummy/', retry_on_404=True)
        self.assertEquals(mock_urlopen.call_count, 1)

        # retry on, retry_on_404 off
        count = []
        mock_urlopen.reset_mock()
        with mock.patch('scrapelib.urllib_urlopen', mock_urlopen):
            s = scrapelib.Scraper(retry_attempts=2, retry_wait_seconds=0.001,
                                  follow_robots=False)
            self.assertRaises(scrapelib.urllib_URLError,
                              s.urlopen, 'ftp://dummy/')
        self.assertEquals(mock_urlopen.call_count, 1)

    def test_ftp_method_restrictions(self):
        # only http(s) supports non-'GET' requests
        self.assertRaises(scrapelib.HTTPMethodUnavailableError,
                          lambda: self.s.urlopen("ftp://dummy/",
                                                 method='POST'))


if __name__ == '__main__':
    unittest.main()
