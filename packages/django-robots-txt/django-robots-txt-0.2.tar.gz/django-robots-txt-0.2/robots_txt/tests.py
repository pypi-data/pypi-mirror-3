from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class RobotsTextTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_robotstxt_can_be_accesses(self):
        url = '/robots.txt'
        r = self.client.get(url)
        self.assertEqual(
            r.status_code,
            200,
            "Couldn't access %s, got %d" % (url, r.status_code)
        )

    def test_robotstxt_has_text_plain_content_type(self):
        url = '/robots.txt'
        r = self.client.get(url)
        self.assertEqual(
            r['Content-Type'],
            'text/plain',
            "Got %s content type for robots.txt" % r['Content-Type']
        )
