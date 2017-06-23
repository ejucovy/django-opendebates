from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import patch

from opendebates.admin import SubmissionAdmin
from opendebates.models import Submission
from opendebates.tests.factories import SubmissionFactory, UserFactory


# mock objects to make the admin think we're superusers.
# mostly copied from
# https://github.com/django/django/blob/master/tests/modeladmin/tests.py#L23-L32

class MockRequest(object):
    POST = {}
    META = {}


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

    def is_authenticated(self):
        return True

request = MockRequest()
request.user = MockSuperUser()


class RemoveSubmissionsTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = SubmissionAdmin(Submission, self.site)
        self.password = 'secretpassword'
        self.user = UserFactory(password=self.password, is_staff=True, is_superuser=True)
        assert self.client.login(username=self.user.username, password=self.password)
        self.submission = SubmissionFactory()
        self.queryset = Submission.objects.all()
        self.changelist_url = reverse('admin:opendebates_submission_changelist')

    def test_get(self):
        """
        GETting the intermediate page should have specified text and the PK of
        the chosen submissions.
        """
        rsp = self.admin.remove_submissions(request, self.queryset)
        self.assertEqual(rsp.status_code, 200)
        self.assertContains(rsp, 'remove the selected submissions?')
        self.assertContains(rsp, self.submission.pk)

    @patch('opendebates.admin.send_email')
    def test_post(self, mock_send_email):
        """
        POSTing the form should cause submissions to be removed and email to be
        sent.
        """
        data = {
            'post': 'Yes',
            'action': 'remove_submissions',
            '_selected_action': [self.submission.pk, ]
        }
        rsp = self.client.post(self.changelist_url, data=data)
        self.assertRedirects(rsp, self.changelist_url)
        # Now submission should not be approved
        submission = Submission.objects.get()
        self.assertFalse(submission.approved)
        # and 1 email should have been sent
        self.assertEqual(mock_send_email.call_count, 1)

    @patch('opendebates.admin.send_email')
    def test_post_multiple(self, mock_send_email):
        "POSTing multiple submissions works as well."
        data = {
            'post': 'Yes',
            'action': 'remove_submissions',
            '_selected_action': [SubmissionFactory().pk, SubmissionFactory().pk]
        }
        rsp = self.client.post(self.changelist_url, data=data)
        self.assertRedirects(rsp, self.changelist_url)
        removed_submissions = Submission.objects.filter(approved=False)
        self.assertEqual(removed_submissions.count(), 2)
        untouched_submission = Submission.objects.filter(approved=True)
        self.assertEqual(untouched_submission.count(), 1)
        # and 2 emails have been sent
        self.assertEqual(mock_send_email.call_count, 2)

    @patch('opendebates.admin.send_email')
    def test_dont_send_email_if_already_unapproved(self, mock_send_email):
        "If submission was already unapproved, don't bug the user again."
        data = {
            'post': 'Yes',
            'action': 'remove_submissions',
            '_selected_action': [SubmissionFactory(approved=False).pk]
        }
        rsp = self.client.post(self.changelist_url, data=data)
        self.assertRedirects(rsp, self.changelist_url)
        removed_submissions = Submission.objects.filter(approved=False)
        self.assertEqual(removed_submissions.count(), 1)
        # and ZERO emails have been sent
        self.assertEqual(mock_send_email.call_count, 0)