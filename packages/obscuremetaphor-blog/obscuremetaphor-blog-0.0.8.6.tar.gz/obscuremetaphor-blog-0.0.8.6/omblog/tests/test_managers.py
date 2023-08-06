# -*- coding: utf-8 -*-
from django.test import TestCase
from omblog.models import Post

class ManagerTestCases(TestCase):
    
    def setUp(self):
        self.p1 = Post(
            title='test post',
            source_content='test',
            slug='test1')
        self.p1.save()
    
    def tearDown(self):
        self.p1.status = Post.DRAFT
        self.p1.save()

    #
    # TODO: test the visible manager method
    #

    def test_published(self):
        """published manager method returns only published blog posts"""
        # none
        self.assertEqual(0, Post.objects.published().count())
        # set to published
        self.p1.status = Post.PUBLISHED
        self.p1.save()
        # now one
        self.assertEqual(1, Post.objects.published().count())

    def test_idea(self):
        """published manager method returns only idea blog posts"""
        # one
        self.assertEqual(1, Post.objects.idea().count())
        # set to published
        self.p1.status = Post.PUBLISHED
        self.p1.save()
        # now none
        self.assertEqual(0, Post.objects.idea().count())

    def test_draft(self):
        """published manager method returns only draft blog posts"""
        # none
        self.assertEqual(0, Post.objects.draft().count())
        # set to published
        self.p1.status = Post.DRAFT
        self.p1.save()
        # now one
        self.assertEqual(1, Post.objects.draft().count())

    def test_hidden(self):
        """published manager method returns only hidden blog posts"""
        # none
        self.assertEqual(0, Post.objects.hidden().count())
        # set to published
        self.p1.status = Post.HIDDEN
        self.p1.save()
        # now one
        self.assertEqual(1, Post.objects.hidden().count())


