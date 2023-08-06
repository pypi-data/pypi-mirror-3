from django.db.models import *
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.template import Context, Template

class ReviewManager(models.Manager):
    def get_query_set(self):
        return super(ReviewManager, self).get_query_set().select_related()

class Review(models.Model):
    """

    """
    class Meta:
        ordering = ["-due_date", "active"]
        verbose_name_plural = "reviews"

    objects = ReviewManager()

    title = models.CharField(max_length = 200)
    description = models.TextField(blank = True, null = True, default='')
    owner = models.ForeignKey(User)
    due_date = models.DateTimeField(null = True, blank = True)
    active = models.BooleanField(default = True)
    peers = models.ManyToManyField(User, verbose_name="list of peers", related_name = 'reviews', null = True, blank = True)
    groups = models.ManyToManyField(Group, verbose_name="list of groups", null = True, blank = True)
    option_group = models.ForeignKey('ReviewOptionGroup')
    content_type = models.ForeignKey(ContentType)
    visible = models.BooleanField(default = False)
    show_reviews_from_peers = models.BooleanField(default = False)
    pagination_count = models.PositiveIntegerField(default = 20)

    def __unicode__(self):
        return self.title

    def get_items(self):
        if self.option_group.score_based:
            return self.items.select_related().annotate(score = Sum('entries__selected_option__value')).order_by('-score')
        else:
            return self.items.select_related().all()

    def save(self, *args, **kwargs):
        super(Review, self).save(*args, **kwargs)

    def response_stats(self):
        item_count = self.items.count()
        peers = list(self.peers.all())
        for group in self.groups.all():
            for peer in group.user_set.all():
                if not peer in peers:
                    peers.append(peer)

        result = {'No response': 0}
        for option in self.option_group.options.all():
            result[option.text] = 0

        responses = 0
        for entry in ReviewEntry.objects.select_related().filter(item__review = self):
            result[entry.selected_option.text] += 1
            responses += 1

        result['No response'] = item_count * len(peers) - responses
        return result


class ReviewOptionGroup(models.Model):
    """

    """
    title = models.CharField(max_length = 200, blank = True, null = True, default='')
    prefix = models.CharField(max_length = 200, blank = True, null = True, default='Your response:')
    entry_formatting = models.TextField(blank = True, null = True, default='{{ date|date:"SHORT_DATE_FORMAT" }}: {{ peer.username }} says {{ selected_option.text }}')
    score_based = models.BooleanField(default = False)
    comments_enabled = models.BooleanField(default = False)
    hide_review_box = models.BooleanField(default=False)

    # help texts:
    prefix.help_text = "This piece of text will appear in front of the optiongroup when rendered, like 'Your response: [related options shown here]'."
    entry_formatting.help_text = "This template will be used by the review 'get_review_entries'-template tag to format entries from users."
    score_based.help_text = "Assigning a value to each option in this group makes it possible to sort reviewed items by score later."
    comments_enabled.help_text = "Can the peer enter a comment or not."
    hide_review_box.help_text = "If checked the user must click a label to perform the review, leaving more place for the items being reviewed."

    def __unicode__(self):
        return self.title

    def add_option(self, text, description = None, sort_index = None, value = None):
        #if self.score_based and not value:

        return ReviewOption.objects.create(optiongroup = self, text = text, description = description, sort_index = sort_index, value = value)

#    def formatted(self, peer):
#        if not self.option_formatting:
#            return 'No formatting specified.'
#
#        c = Context(dict(title = self.title, description = self.description, score_based = self.score_based, options = self.options.all()))
#        return Template(self.option_formatting).render(c)

icon_choices = [
    ('icon-adjust', 'adjust'),
    ('icon-align-center', 'align-center'),
    ('icon-align-justify', 'align-justify'),
    ('icon-align-left', 'align-left'),
    ('icon-align-right', 'align-right'),
    ('icon-arrow-down', 'arrow-down'),
    ('icon-arrow-left', 'arrow-left'),
    ('icon-arrow-right', 'arrow-right'),
    ('icon-arrow-up', 'arrow-up'),
    ('icon-asterisk', 'asterisk'),
    ('icon-backward', 'backward'),
    ('icon-ban-circle', 'ban-circle'),
    ('icon-barcode', 'barcode'),
    ('icon-bell', 'bell'),
    ('icon-bold', 'bold'),
    ('icon-book', 'book'),
    ('icon-bookmark', 'bookmark'),
    ('icon-briefcase', 'briefcase'),
    ('icon-bullhorn', 'bullhorn'),
    ('icon-calendar', 'calendar'),
    ('icon-camera', 'camera'),
    ('icon-certificate', 'certificate'),
    ('icon-check', 'check'),
    ('icon-chevron-down', 'chevron-down'),
    ('icon-chevron-left', 'chevron-left'),
    ('icon-chevron-right', 'chevron-right'),
    ('icon-chevron-up', 'chevron-up'),
    ('icon-circle-arrow-down', 'circle-arrow-down'),
    ('icon-circle-arrow-left', 'circle-arrow-left'),
    ('icon-circle-arrow-right', 'circle-arrow-right'),
    ('icon-circle-arrow-up', 'circle-arrow-up'),
    ('icon-cog', 'cog'),
    ('icon-comment', 'comment'),
    ('icon-download', 'download'),
    ('icon-download-alt', 'download-alt'),
    ('icon-edit', 'edit'),
    ('icon-eject', 'eject'),
    ('icon-envelope', 'envelope'),
    ('icon-exclamation-sign', 'exclamation-sign'),
    ('icon-eye-close', 'eye-close'),
    ('icon-eye-open', 'eye-open'),
    ('icon-facetime-video', 'facetime-video'),
    ('icon-fast-backward', 'fast-backward'),
    ('icon-fast-forward', 'fast-forward'),
    ('icon-file', 'file'),
    ('icon-film', 'film'),
    ('icon-filter', 'filter'),
    ('icon-fire', 'fire'),
    ('icon-flag', 'flag'),
    ('icon-folder-close', 'folder-close'),
    ('icon-folder-open', 'folder-open'),
    ('icon-font', 'font'),
    ('icon-forward', 'forward'),
    ('icon-fullscreen', 'fullscreen'),
    ('icon-gift', 'gift'),
    ('icon-globe', 'globe'),
    ('icon-hand-down', 'hand-down'),
    ('icon-hand-left', 'hand-left'),
    ('icon-hand-right', 'hand-right'),
    ('icon-hand-up', 'hand-up'),
    ('icon-hdd', 'hdd'),
    ('icon-headphones', 'headphones'),
    ('icon-heart', 'heart'),
    ('icon-home', 'home'),
    ('icon-inbox', 'inbox'),
    ('icon-indent-left', 'indent-left'),
    ('icon-indent-right', 'indent-right'),
    ('icon-info-sign', 'info-sign'),
    ('icon-italic', 'italic'),
    ('icon-leaf', 'leaf'),
    ('icon-list', 'list'),
    ('icon-list-alt', 'list-alt'),
    ('icon-lock', 'lock'),
    ('icon-magnet', 'magnet'),
    ('icon-map-marker', 'map-marker'),
    ('icon-minus', 'minus'),
    ('icon-minus-sign', 'minus-sign'),
    ('icon-move', 'move'),
    ('icon-music', 'music'),
    ('icon-off', 'off'),
    ('icon-ok', 'ok'),
    ('icon-ok-circle', 'ok-circle'),
    ('icon-ok-sign', 'ok-sign'),
    ('icon-pause', 'pause'),
    ('icon-pencil', 'pencil'),
    ('icon-picture', 'picture'),
    ('icon-plane', 'plane'),
    ('icon-play', 'play'),
    ('icon-play-circle', 'play-circle'),
    ('icon-plus', 'plus'),
    ('icon-plus-sign', 'plus-sign'),
    ('icon-print', 'print'),
    ('icon-qrcode', 'qrcode'),
    ('icon-question-sign', 'question-sign'),
    ('icon-random', 'random'),
    ('icon-refresh', 'refresh'),
    ('icon-remove', 'remove'),
    ('icon-remove-circle', 'remove-circle'),
    ('icon-remove-sign', 'remove-sign'),
    ('icon-repeat', 'repeat'),
    ('icon-resize-full', 'resize-full'),
    ('icon-resize-horizontal', 'resize-horizontal'),
    ('icon-resize-small', 'resize-small'),
    ('icon-resize-vertical', 'resize-vertical'),
    ('icon-retweet', 'retweet'),
    ('icon-road', 'road'),
    ('icon-screenshot', 'screenshot'),
    ('icon-search', 'search'),
    ('icon-share', 'share'),
    ('icon-share-alt', 'share-alt'),
    ('icon-shopping-cart', 'shopping-cart'),
    ('icon-signal', 'signal'),
    ('icon-star', 'star'),
    ('icon-star-empty', 'star-empty'),
    ('icon-step-backward', 'step-backward'),
    ('icon-step-forward', 'step-forward'),
    ('icon-stop', 'stop'),
    ('icon-tag', 'tag'),
    ('icon-tags', 'tags'),
    ('icon-tasks', 'tasks'),
    ('icon-text-height', 'text-height'),
    ('icon-text-width', 'text-width'),
    ('icon-th', 'th'),
    ('icon-th-large', 'th-large'),
    ('icon-th-list', 'th-list'),
    ('icon-thumbs-down', 'thumbs-down'),
    ('icon-thumbs-up', 'thumbs-up'),
    ('icon-time', 'time'),
    ('icon-tint', 'tint'),
    ('icon-trash', 'trash'),
    ('icon-upload', 'upload'),
    ('icon-user', 'user'),
    ('icon-volume-down', 'volume-down'),
    ('icon-volume-off', 'volume-off'),
    ('icon-volume-up', 'volume-up'),
    ('icon-warning-sign', 'warning-sign'),
    ('icon-wrench', 'wrench'),
    ('icon-zoom-in', 'zoom-in'),
    ('icon-zoom-out', 'zoom-out'),
    ('icon-glass', 'glass'),
]


class ReviewOptionManager(models.Manager):
    def get_query_set(self):
        return super(ReviewOptionManager, self).get_query_set().select_related()

class ReviewOption(models.Model):
    """

    """
    class Meta:
        ordering = ('sort_index','value', 'text',)
        verbose_name = 'review option'
        verbose_name_plural = 'review options'

    objects = ReviewOptionManager()

    optiongroup = models.ForeignKey('ReviewOptionGroup', related_name='options')
    text = models.CharField(max_length = 200, blank = True, null = True, default='')
    description = models.CharField(max_length = 500, blank = True, null = True, default='')
    value = models.IntegerField(default = 0)
    sort_index = models.IntegerField(default = 0)
    icon = models.CharField(max_length = 50, blank = True, null = True, default='', choices = icon_choices)

    # help texts
    icon.help_text = "Go to http://twitter.github.com/bootstrap/base-css.html#icons for details."

    def __unicode__(self):
        return self.text

    def entries(self, content_type = None, review = None, order_by = None):
        qs = ReviewItem.objects.filter(entries__selected_option = self)

        if content_type:
            qs = qs.filter(content_type = content_type)

        if review:
            qs = qs.filter(review = review)

        if order_by:
            qs.order_by(order_by)

        return qs

class ReviewItemManager(models.Manager):
    def get_query_set(self):
        return super(ReviewItemManager, self).get_query_set().select_related()

class ReviewItem(models.Model):
    """

    """
    #class Meta:
    #    ordering = ('value', 'text',)
    #    verbose_name = 'review option'
    #    verbose_name_plural = 'review options'

    objects = ReviewItemManager()

    review = models.ForeignKey('Review', related_name = 'items')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "%s [%s] - %s" % (self.review.title, self.content_type, self.content)


class ReviewEntryManager(models.Manager):
    def get_query_set(self):
        return super(ReviewEntryManager, self).get_query_set().select_related()


class ReviewEntry(models.Model):
    """

    """
    #class Meta:
    #    ordering = ('value', 'text',)
    #    verbose_name = 'review option'
    #    verbose_name_plural = 'review options'

    item = models.ForeignKey('ReviewItem', related_name='entries')
    selected_option = models.ForeignKey('ReviewOption')
    peer = models.ForeignKey(User)
    date = models.DateTimeField(blank = True, null = True, auto_now = True)
    comment = models.TextField(null = True, blank = True)

    objects = ReviewEntryManager()

    def __str__(self):
        option_group = self.item.review.option_group
        t = Template(option_group.entry_formatting)
        c = Context(dict(
            peer = self.peer,
            selected_option = self.selected_option,
            date = self.date,
            comment = self.comment
        ))
        return t.render(c)