#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
from django.core.mail import EmailMessage
from django.db.models import Q

from models import *


class ReviewFluent:
    """

    """
    def __init__(self, title):
        self.title = title
        self.owner = None
        self.peers = []
        self.groups = []
        self.items = []
        self.ct = None
        self.og = None

    @classmethod
    def new(cls, title):
        return ReviewFluent(title)

    def created_by(self, user):
        self.owner = user
        return self

    def reviewed_by(self, *peers):
        for peer in peers:
            if not peer in self.peers:
                self.peers.append(peer)
        return self

    def of(self, content_type):
        self.ct = content_type
        return self

    def option_group(self, option_group):
        self.og = option_group
        return self

    def items_to_review(self, *items):
        for item in items:
            if not item in self.items:
                self.items.append(item)
        return self


class ReviewLogic:
    """

    """
    @classmethod
    def new(cls, title, owner, model, option_group, items = [], peers = []):
        re = Review.objects.create(title = title, content_type = ContentType.objects.get_for_model(model), owner = owner, option_group = option_group)

        if items:
            ReviewLogic.add_items(re, items)

        for peer in peers:
            re.peers.add(peer)

        if peers:
            re.save()

        return re

    @classmethod
    def add_items(cls, review, items):
        content_type = ContentType.objects.get_for_model(items[0])
        items_to_create = []
        for item in items:
            if not review.items.filter(content_type = content_type, object_id = item.id).count():
                items_to_create.append(ReviewItem(review = review, content = item))
        ReviewItem.objects.bulk_create(items_to_create)

        review.save()

    @classmethod
    def can_add_entry(cls, review, peer):
        if (review.peers.filter(username = peer.username).count()):
            return True

        for group in peer.groups.all():
            if group in review.groups.all():
                return True

        return False

    @classmethod
    def owned_by(cls, owner):
        return Review.objects.filter(owner = owner, active = True)

    @classmethod
    def get_progress_for_user(cls, review, peer):
        return (review.items.all().count(), review.items.filter(entries__peer__in = (peer,)).count())

    @classmethod
    def assign_progress(cls, review, peer):
        total_count, current_status = cls.get_progress_for_user(review, peer)
        setattr(review, 'progress_for_user', "%s of %s done. %0.2f %% completed." % (current_status, total_count,  (current_status / total_count) * 100))
        setattr(review, 'progress_values', (total_count, current_status))

    @classmethod
    def active_reviews_for_peer(cls, peer):
        for review in Review.objects.select_related().filter(Q(active = True) & (Q(peers__id__in = (peer.id,)) | Q(groups__id__in = peer.groups.all()))):
            cls.assign_progress(review, peer)
            yield review

    @classmethod
    def add_entry(cls, review, model_instance, peer, review_option, comment = None):
        if not ReviewLogic.can_add_entry(review, peer):
            raise Exception('You are not allowed to review this item')

        content_type = ContentType.objects.get_for_model(model_instance)
        item_to_review = None
        for item in review.items.all():
            if item.content.id == model_instance.id and item.content_type == content_type:
                item_to_review = item

        if not item_to_review:
            raise Exception('Could not find item to review.')

        if review.option_group and review.option_group != review_option.optiongroup:
            raise Exception('Wrong option-group for review.')

        entries = item_to_review.entries.filter(peer = peer)
        if not list(entries):
            entry = ReviewEntry.objects.create(peer = peer, item = item_to_review, selected_option = review_option, comment = comment)
        else:
            entry = entries[0]
            entry.selected_option = review_option
            entry.comment = comment
            entry.save()

        return entry


class ReviewOptionLogic:
    """

    """
    @classmethod
    def new_group(cls, title, score_based = False, options = []):
        rog = ReviewOptionGroup.objects.create(title = title, score_based = score_based)
        if options:
            ReviewOption.objects.bulk_create([ReviewOption(optiongroup = rog, text = opt) for opt in options])

        return rog

    @classmethod
    def new_option(cls, optiongroup, text, description = None, sort_index = None, value = None, icon = None):
        return ReviewOption.objects.create(optiongroup = optiongroup, text = text, description = description, sort_index = sort_index, value = value, icon = icon)


class ReviewDetails:
    """

    """
    def __init__(self, review_id, peer):
        self.peer = peer
        self.review = Review.objects.select_related().get(id = review_id)

    def items(self):
        return self.review.items.all()

    @property
    def content_type(self):
        return self.review.content_type

    @property
    def pagination_count(self):
        return self.review.pagination_count


class ReviewsForPeer:
    """

    """
    def __init__(self, peer):
        self.reviews_not_started = []
        self.reviews_started = []
        self.reviews_finished = []

        for review in ReviewLogic.active_reviews_for_peer(peer):
            total_count, current_status = review.progress_values
            if total_count == current_status:
                self.reviews_finished.append(review)
            elif current_status == 0:
                self.reviews_not_started.append(review)
            elif total_count > current_status and current_status > 0:
                self.reviews_started.append(review)

        print vars(self)

class SendingEmail:
    """

    """
    def __init__(self, subject, message, email_addresses):
        email = EmailMessage(subject, message, t=email_addresses)
        email.save()