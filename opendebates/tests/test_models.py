from django.test import TestCase, override_settings
import urlparse

from .factories import UserFactory, VoterFactory, SubmissionFactory


@override_settings(SITE_DOMAIN_WITH_PROTOCOL="https://example.net")
class SubmissionReallyAbsoluteUrlTest(TestCase):

    def setUp(self):
        self.submission = SubmissionFactory()
        self.id = self.submission.id

    def test_default(self):
        self.assertEqual('https://example.net/questions/%s/vote/' % self.id,
                         self.submission.really_absolute_url())

    def test_source(self):
        url = self.submission.really_absolute_url("fb")

        # When a source is included, nothing before querystring is affected
        self.assertEqual(self.submission.really_absolute_url(),
                         url.split('?')[0])

        # The query string will include a ?source parameter prefixed with share-
        # that includes both the platform we are sharing on, and the question ID
        parsed = urlparse.urlparse(url)
        self.assertEqual(parsed.query, 'source=share-fb-%s' % self.id)

        parsed = urlparse.urlparse(self.submission.really_absolute_url('foo'))
        self.assertEqual(parsed.query, 'source=share-foo-%s' % self.id)


class VoterUserDisplayNameTest(TestCase):

    def test_anonymous(self):
        voter = VoterFactory(user=None)
        self.assertEqual('Somebody', str(voter.user_display_name()))

    def test_user_blank(self):
        user = UserFactory(first_name='', last_name='')
        voter = VoterFactory(user=user)
        self.assertEqual('Somebody', str(voter.user_display_name()))

    def test_user_no_last_name(self):
        user = UserFactory(first_name='George', last_name='')
        voter = VoterFactory(user=user)
        self.assertEqual('George', str(voter.user_display_name()))

    def test_user_both_names(self):
        user = UserFactory(first_name='George', last_name='Washington')
        voter = VoterFactory(user=user)
        self.assertEqual('George W.', str(voter.user_display_name()))

    def test_user_with_state(self):
        user = UserFactory(first_name='George', last_name='Washington')
        voter = VoterFactory(user=user, state='VA')
        self.assertEqual('George W. from VA', str(voter.user_display_name()))

    def test_user_with_explicit_display_name(self):
        user = UserFactory(first_name='George', last_name='Washington')
        voter = VoterFactory(user=user, display_name='Prez1')
        self.assertEqual('Prez1', str(voter.user_display_name()))

    def test_voter_with_explicit_display_name_with_state(self):
        user = UserFactory(first_name='George', last_name='Washington')
        voter = VoterFactory(user=user, display_name='Prez1', state='VA')
        self.assertEqual('Prez1 from VA', str(voter.user_display_name()))
