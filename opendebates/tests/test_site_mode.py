from django.test import TestCase

from opendebates.models import SiteMode


class AnnouncementTest(TestCase):

    def setUp(self):
        self.mode, _ = SiteMode.objects.get_or_create()
        self.mode.save()
        self.url = '/'

    def test_default_no_announcement(self):
        rsp = self.client.get(self.url)
        self.assertNotIn('<div class="site-announcement warning">', rsp.content)

    def test_announcement_headline(self):
        headline = "Announcement: tune in tonight!"
        self.mode.announcement_headline = headline
        self.mode.save()

        rsp = self.client.get(self.url)
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn(headline, rsp.content)

    def test_announcement_body(self):
        headline = "Announcement: tune in tonight!"
        body = "Don't forget to watch."
        self.mode.announcement_headline = headline
        self.mode.announcement_body = body
        self.mode.save()

        rsp = self.client.get(self.url)
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn(body, rsp.content)

    def test_no_announcement_if_no_headline(self):
        body = "Announcement: tune in tonight!"
        self.mode.announcement_headline = None
        self.mode.announcement_body = body
        self.mode.announcement_link = "http://example.com"
        self.mode.save()

        rsp = self.client.get(self.url)
        self.assertNotIn('<div class="site-announcement warning">', rsp.content)
        self.assertNotIn(body, rsp.content)

    def test_announcement_link(self):
        headline = "Announcement: tune in tonight!"
        link = "http://example.com/the-special-page"
        self.mode.announcement_headline = headline
        self.mode.announcement_link = link
        self.mode.save()

        rsp = self.client.get(self.url)
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn('<a href="%s">' % link, rsp.content)

    def test_announcement_page_regex(self):
        headline = "Announcement: tune in tonight!"
        link = "http://example.com/the-special-page"
        self.mode.announcement_headline = headline
        self.mode.announcement_link = link
        self.mode.announcement_page_regex = "/registration/"
        self.mode.save()

        rsp = self.client.get('/registration/register/')
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn('<a href="%s">' % link, rsp.content)

        rsp = self.client.get('/')
        self.assertNotIn('<div class="site-announcement warning">', rsp.content)
        self.assertNotIn('<a href="%s">' % link, rsp.content)

        self.mode.announcement_page_regex = "^(?!/registration/register/).*$"
        self.mode.save()

        rsp = self.client.get('/registration/register/')
        self.assertNotIn('<div class="site-announcement warning">', rsp.content)
        self.assertNotIn('<a href="%s">' % link, rsp.content)

        rsp = self.client.get('/registration/login/')
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn('<a href="%s">' % link, rsp.content)

        rsp = self.client.get('/')
        self.assertIn('<div class="site-announcement warning">', rsp.content)
        self.assertIn('<a href="%s">' % link, rsp.content)
