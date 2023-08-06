# coding: utf-8

from __future__ import absolute_import


from django.core import mail
from sentry.models import Project, ProjectMember, Group, Event, \
  MessageFilterValue, MessageCountByMinute, FilterValue, PendingProjectMember

from tests.base import TestCase


class ProjectTest(TestCase):
    fixtures = ['tests/fixtures/views.json']

    def setUp(self):
        self.project = Project.objects.get(id=1)

    def test_migrate(self):
        project2 = Project.objects.create(name='Test')
        self.project.merge_to(project2)

        self.assertFalse(Project.objects.filter(pk=1).exists())
        self.assertFalse(Group.objects.filter(project__isnull=True).exists())
        self.assertFalse(Event.objects.filter(project__isnull=True).exists())
        self.assertFalse(MessageFilterValue.objects.filter(project__isnull=True).exists())
        self.assertFalse(MessageCountByMinute.objects.filter(project__isnull=True).exists())
        self.assertFalse(FilterValue.objects.filter(project__isnull=True).exists())

        self.assertEquals(project2.group_set.count(), 4)
        self.assertEquals(project2.event_set.count(), 10)
        self.assertEquals(project2.messagefiltervalue_set.count(), 0)
        self.assertEquals(project2.messagecountbyminute_set.count(), 0)
        self.assertEquals(project2.filtervalue_set.count(), 0)


class ProjectMemberTest(TestCase):
    fixtures = ['tests/fixtures/views.json']

    def test_get_dsn(self):
        member = ProjectMember(project_id=1, public_key='public', secret_key='secret')
        with self.Settings(SENTRY_URL_PREFIX='http://example.com'):
            self.assertEquals(member.get_dsn(), 'http://public:secret@example.com/1')

    def test_get_dsn_with_ssl(self):
        member = ProjectMember(project_id=1, public_key='public', secret_key='secret')
        with self.Settings(SENTRY_URL_PREFIX='https://example.com'):
            self.assertEquals(member.get_dsn(), 'https://public:secret@example.com/1')

    def test_get_dsn_with_port(self):
        member = ProjectMember(project_id=1, public_key='public', secret_key='secret')
        with self.Settings(SENTRY_URL_PREFIX='http://example.com:81'):
            self.assertEquals(member.get_dsn(), 'http://public:secret@example.com:81/1')


class PendingProjectMemberTest(TestCase):
    fixtures = ['tests/fixtures/views.json']

    def test_token_generation(self):
        member = PendingProjectMember(id=1, project_id=1, email='foo@example.com')
        with self.Settings(SENTRY_KEY='a'):
            self.assertEquals(member.token, 'f3f2aa3e57f4b936dfd4f42c38db003e')

    def test_token_generation_unicode_key(self):
        member = PendingProjectMember(id=1, project_id=1, email='foo@example.com')
        with self.Settings(SENTRY_KEY="\xfc]C\x8a\xd2\x93\x04\x00\x81\xeak\x94\x02H\x1d\xcc&P'q\x12\xa2\xc0\xf2v\x7f\xbb*lX"):
            self.assertEquals(member.token, 'df41d9dfd4ba25d745321e654e15b5d0')

    def test_send_invite_email(self):
        member = PendingProjectMember(id=1, project_id=1, email='foo@example.com')
        with self.Settings(SENTRY_URL_PREFIX='http://example.com'):
            member.send_invite_email()

            self.assertEquals(len(mail.outbox), 1)

            msg = mail.outbox[0]

            self.assertEquals(msg.to, ['foo@example.com'])
