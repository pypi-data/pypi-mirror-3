from django.db import models
from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from peerreview.logic import *

class Joke(models.Model):
    """

    """
    text = models.CharField(max_length=100)

    def __unicode__(self):
        return self.text

class Quote(models.Model):
    """

    """
    text = models.CharField(max_length = 400)
    source = models.CharField(max_length = 200)

def create_user(username):
    return User.objects.create_user(username, '%s@test.com' % username, 'password')

class SimpleTest(TestCase):

    def setUp(self):
        self.joe = create_user('joe')
        self.jane = create_user('jane')
        self.roy = create_user('roy')
        self.tom = create_user('tom')

        self.review_group = Group.objects.create(name = 'Reviewers')
        self.jane.groups.add(self.review_group)
        self.joe.groups.add(self.review_group)

        self.joke_rog = ReviewOptionLogic.new_group('Joke review')
        self.terrible_joke = ReviewOptionLogic.new_option(self.joke_rog, 'Terrible')
        self.ok_joke = ReviewOptionLogic.new_option(self.joke_rog, 'Ok')
        self.great_joke = ReviewOptionLogic.new_option(self.joke_rog, 'Great')

        self.joke1 = Joke.objects.create(text = 'joke 1')
        self.joke2 = Joke.objects.create(text = 'joke 2')
        self.joke3 = Joke.objects.create(text = 'joke 3')
        self.joke4 = Joke.objects.create(text = 'joke 4')

    def test_fluent_review(self):
        review = ReviewFluent('Review of good jokes')
        review.of(Joke).created_by(self.joe).\
                    option_group(self.joke_rog).\
                    reviewed_by(self.joe, self.jane, self.tom).\
                    items_to_review(self.joke1, self.joke2, self.joke3)

        #print vars(review)

    def test_review_groups(self):
        r1 = ReviewLogic.new('Review #1', self.joe, Joke, self.joke_rog, (self.joke4,))
        r1.groups.add(self.review_group)
        r1.save()

        ReviewLogic.add_entry(r1, self.joke4, self.jane, self.terrible_joke)
        ReviewLogic.add_entry(r1, self.joke4, self.joe, self.terrible_joke)
        #self.assertRaises(Exception, r1.add_entry(joke4, self.roy, terrible_joke))

    def test_needs_attention_by_group(self):
        r1 = ReviewLogic.new('Review #1', self.joe, Joke, self.joke_rog, (self.joke4,))
        r1.groups.add(self.review_group)
        r1.save()

        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.jane))), 1)
        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.joe))), 1)
        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.tom))), 0)

    def test_client(self):
        self.assertEqual(Review.objects.all().count(), 0)

        r1 = ReviewLogic.new('Review #1', self.joe, Joke, self.joke_rog, (self.joke1, self.joke2, self.joke3, self.joke4), (self.jane, self.roy, self.tom, self.joe))
        self.assertEqual(len(self.terrible_joke.entries()), 0)

        c = Client()
        self.assertEqual(c.login(username=self.joe.username, password='password'), True)
        response = c.post(reverse('peer-review-add-entry', args=(r1.id, ContentType.objects.get_for_model(Joke).name, self.joke1.id, self.terrible_joke.id)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.all().count(), 1)
        self.assertEqual(ReviewEntry.objects.all().count(), 1)
        self.assertEqual(len(self.terrible_joke.entries()), 1)

    def test_needs_attention(self):
        r1 = ReviewLogic.new('Review #1', self.joe, Joke, self.joke_rog, (self.joke1, self.joke2, self.joke3, self.joke4), (self.jane, self.roy))
        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.jane))), 1)
        # not in list of peers, has no review
        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.tom))), 0)
        # Reviews by owner filtered out
        self.assertEqual(len(list(ReviewLogic.active_reviews_for_peer(self.joe))), 0)

    def test_review_grouping(self):
        r1 = ReviewLogic.new('Review #1', self.joe, Joke, self.joke_rog, (self.joke4, self.joke1, self.joke2, self.joke3))
        r1.groups.add(self.review_group)
        r1.save()

        ReviewLogic.add_entry(r1, self.joke1, self.jane, self.terrible_joke)
        ReviewLogic.add_entry(r1, self.joke1, self.joe, self.great_joke)

        ReviewLogic.add_entry(r1, self.joke2, self.jane, self.terrible_joke)
        ReviewLogic.add_entry(r1, self.joke2, self.joe, self.ok_joke)

        self.assertEqual(r1.progress_percent, 50)

        ReviewLogic.add_entry(r1, self.joke3, self.jane, self.terrible_joke)
        ReviewLogic.add_entry(r1, self.joke3, self.joe, self.terrible_joke)

        self.assertEqual(r1.progress_percent, 75)

        ReviewLogic.add_entry(r1, self.joke4, self.jane, self.terrible_joke)
        ReviewLogic.add_entry(r1, self.joke4, self.joe, self.terrible_joke)

        self.assertEqual(r1.progress_percent, 100)

    def tearDown(self):
        self.joe.delete()
        self.jane.delete()
        self.roy.delete()
        self.tom.delete()
        self.review_group.delete()
        self.joke_rog.delete()
        self.terrible_joke.delete()
        self.ok_joke.delete()
        self.great_joke.delete()
        self.joke1.delete()
        self.joke2.delete()
        self.joke3.delete()
        self.joke4.delete()
