from __future__ import division
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Q
from peerreview.models import *
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

models_to_exclude = ['user', 'group', 'review', 'content type', 'log entry', 'permission', 'review item', 'review entry', 'review option', 'review option group', 'session', 'site']

class ReviewListFilter(SimpleListFilter):
    title = _('content type')
    parameter_name = 'reviewfilter'

    def lookups(self, request, model_admin):
        result = []
        for ct in ContentType.objects.exclude(name__in = models_to_exclude):
            result.append((ct.name, ct.name))
        return tuple(result)

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset

        return queryset.filter(content_type__name = val)

class ReviewStatusListFilter(SimpleListFilter):
    title = _('Review status')
    parameter_name = 'reviewstatusfilter'

    def lookups(self, request, model_admin):
        return (
            ('yours', 'Your reviews'),
            ('assigned', 'Assigned to you'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset

        if val == 'yours':
            return queryset.filter(owner = request.user)
        elif val == 'assigned':
            return queryset.filter(peers__in = (request.user,))
        else:
            return queryset

class ReviewItemAdmin(admin.TabularInline):
    model = ReviewItem


class ReviewAdminForm(ModelForm):
    class Meta:
        model = Review
        exclude = ('owner',)

    def __init__(self, *args, **kwargs):
        super(ReviewAdminForm, self).__init__(*args, **kwargs)
        #review = kwargs.get('instance')
        if self.fields.has_key('content_type'):
            content_types = ContentType.objects.exclude(name__in = models_to_exclude)
            w = self.fields['content_type'].widget
            choices = []
            for content_type in content_types:
                choices.append((content_type.id, content_type.name))
            w.choices = choices

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'add_items_link', 'view_items_link', 'owner', )
    list_filter = (ReviewStatusListFilter, 'active', 'option_group', ReviewListFilter,)
    search_fields = ['title', 'description', 'content_type__name', 'option_group__title']
    form = ReviewAdminForm
#    if settings.DEBUG:
#        list_display = list(list_display) + ['item_count']

    def get_readonly_fields(self, request, obj=None):
        return obj and ['content_type', 'option_group'] or []

#    def change_view(self, request, obj_id):
#        print obj_id
#        if obj_id:
#            self.readonly_fields = ('content_type', 'option_group',)
#        return super(ReviewAdmin, self).change_view(request, obj_id)
#
#    def add_view(self, request, form_url='', extra_context=None):
#        return super(ReviewAdmin, self).add_view(request, form_url, extra_context)

    def view_items_link(self, obj):
        try:
            if obj.items.count():
                return '<a href="%s">Review items</a>' % (reverse('peer-review-review-details', args=[obj.id] ))
            return 'No items assigned yet.'
        except Exception, e:
            return e
    view_items_link.allow_tags = True
    view_items_link.short_description = 'Review items'

    def add_items_link(self, obj):
        try:
            return '<a href="%s">%s</a>' % (reverse('admin:%s_%s_changelist' % (obj.content_type.app_label, obj.content_type.name)), obj.content_type.name)
        except Exception, e:
            return e
    add_items_link.allow_tags = True
    add_items_link.short_description = 'Content type ( click to add items)'

    def progress(self, obj):
        item_count = obj.items.all().count() * obj.peers.all().count();
        if item_count == 0:
            return 'No items assigned yet.'

        try:
            items_reviewed = ReviewEntry.objects.filter(item__review = obj).count();
            return ("%s of %s done. %0.2f %% completed." % (items_reviewed, item_count,  (items_reviewed / item_count) * 100))
        except Exception, e:
            return e
    progress.short_description = 'Progress'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()

    def queryset(self, request):
        qs = super(ReviewAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(Q(owner=request.user))# | Q(public = True))

    #def change_view(self, request, object_id, extra_context=None):
    #    result = super(DocumentAdmin, self).change_view(request, object_id, extra_context)
    #    document = models.Document.objects.get(id__exact=object_id)
    #    if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue'):
    #        result['Location'] = document.get_absolute_url()
    #    return result

admin.site.register(Review, ReviewAdmin)


class ReviewOptionAdmin(admin.TabularInline):
    model = ReviewOption
    extra = 2

class ReviewOptionGroupAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = [ReviewOptionAdmin]

admin.site.register(ReviewOptionGroup, ReviewOptionGroupAdmin)


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        exclude = ('owner', 'due_date', 'active',)


def add_items_to_review(modeladmin, request, queryset):
    ct = ContentType.objects.get_for_model(queryset.model)
    ids = [str(p.id) for p in queryset]
    selected_ids = ','.join(ids)
    number_of_items = len(ids)
    #print request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    return render_to_response('peerreview/review_wizard.html', {
            'content_type': ct.name,
            'app_label': ct.app_label,
            'number_of_items': number_of_items,
            'redirect_url': reverse('admin:%s_%s_changelist' % (ct.app_label, ct.name)),
            'selected_ids': selected_ids,
            'reviews_available': Review.objects.filter(content_type = ct, owner = request.user)
        }, context_instance=RequestContext(request))

add_items_to_review_str = "Add selected items to a review"
admin.site.add_action(add_items_to_review, add_items_to_review_str)

if settings.DEBUG:
    admin.site.register(ReviewEntry)
    admin.site.register(ReviewItem)
