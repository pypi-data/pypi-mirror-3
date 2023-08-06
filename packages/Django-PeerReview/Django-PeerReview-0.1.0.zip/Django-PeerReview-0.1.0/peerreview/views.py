from django.contrib.admin.sites import site
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
#from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse_lazy

from peerreview.models import *
from peerreview.logic import *
from peerreview.admin import add_items_to_review_str

from mobilityhelpers import smart_response

@csrf_exempt
@login_required(login_url= reverse_lazy('peer-review-login'))
def post_comment(request):
    if request.is_ajax():
        item_id = int(request.POST.get('item_id'))
        comments = request.POST.get('comments', None)
        ri = ReviewItem.objects.select_related().get(id = item_id)
        entry = None
        if not ri.entries.filter(peer = request.user).count():
            ReviewEntry.objects.create(item = ri, peer = request.user, comment = comments)
        else:
            entry = ReviewEntry.objects.get(peer = request.user, item = ri)
            entry.comment = comments
            entry.save()
        return HttpResponse("Success -> %s!" % entry)
    return HttpResponse("This is an ajax view!")

@csrf_exempt
@login_required(login_url= reverse_lazy('peer-review-login'))
def review_item(request):
    if request.is_ajax():
        option_id = int(request.POST.get('option_id'))
        item_id = int(request.POST.get('item_id'))
        comments = request.POST.get('comments', None)
        ri = ReviewItem.objects.select_related().get(id = item_id)
        entry = None
        if not ri.entries.filter(peer = request.user).count():
            ReviewEntry.objects.create(item = ri, peer = request.user, selected_option_id = option_id, comment = comments)
        else:
            entry = ReviewEntry.objects.get(peer = request.user, item = ri)
            entry.selected_option_id = option_id
            entry.comment = comments
            entry.save()
        return HttpResponse("Success -> %s!" % entry)
    return HttpResponse("This is an ajax view!")

@login_required
def email_remainder(request, review_id):
    return render_to_response('peerreview/frontend/index.html',
        dict(reviewdata = ReviewsForPeer(request.user)),
        context_instance = RequestContext(request))

@login_required
def email_message(request, review_id):
    return render_to_response('admin/peerreview/review/email_message.html',
        dict(review = Review.objects.get(id = review_id)),
        context_instance = RequestContext(request))

def login_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('peer-review-index'))

    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    msg = None
    if user:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('peer-review-index'))
        else:
            msg = 'Account is disabled.'
    else:
        msg = 'Login failed. Check username and/or password.'

    return smart_response(request, 'peerreview/frontend/login.html', dict(msg = msg))


def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('peer-review-login'))

    return smart_response(request, 'peerreview/frontend/index.html',
        dict(reviewdata = ReviewsForPeer(request.user)))

def remove_item_from_review(modeladmin, request, queryset):
    ids = map(int, request.POST.getlist('_selected_action', []))
    ReviewItem.objects.filter(id__in = ids).delete()

remove_item_from_review.short_description = ugettext_lazy("Remove selected items from review")

class GenericListFilter(SimpleListFilter):

    def __init__(self, option_group, title, parameter_name, request, params, model, model_admin):
        self.option_group = option_group
        self._parameter_name = parameter_name
        self._title = title
        super(SimpleListFilter, self).__init__(request, params, model, model_admin)

    def lookups(self, request, model_admin):
        result = []
        for ct in self.option_group.options.all():
            result.append((ct.id, ct.text))
        return tuple(result)

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset

        return queryset.all()

    @property
    def title(self):
        return self._title

    @property
    def parameter_name(self):
        return self._parameter_name

@login_required(login_url= reverse_lazy('peer-review-login'))
def items_list(request, review_id):
    review = Review.objects.select_related().get(id = review_id)
    model_admin = copy.copy(site._registry[review.content_type.model_class()])

    fields = list(model_admin.list_display)
    fields.insert(0, '_item_link_')
    model_admin._item_link_ = lambda x: x._item_link_
    model_admin._item_link_.short_description = 'Link'
    model_admin._item_link_.allow_tags = True

    if review.option_group.score_based:
        fields.append('score')
        model_admin.score = lambda x: x.score
        model_admin.score.short_description = 'Score'

    model_admin.get_list_display = lambda x: fields
    model_admin.actions = list(model_admin.actions)

    model_admin.actions.append(remove_item_from_review)
    actions = model_admin.get_actions(request)
    if actions.has_key(add_items_to_review_str):
        del actions[add_items_to_review_str]

    actions['remove_item_from_review'] = (remove_item_from_review, 'remove_item_from_review', ugettext_lazy('Remove selected items from current review'))
    model_admin.get_actions = lambda x: actions

    #model_admin.list_filter += (GenericListFilter(review.option_group, review.option_group.title, 'filter_%s' % review.option_group.title, request, {}, review.content_type.model_class(), model_admin),)

    res = model_admin.changelist_view(request)
    if not hasattr(res, 'context_data'):
        return res

    cl = res.context_data['cl']
    res.context_data['title'] = ugettext_lazy("Assigned %s ") % cl.opts.verbose_name_plural.capitalize()
    cl.result_list = review.get_items()
    for item in cl.result_list:
        item._item_link_ = '<a href="%s">%s</a>' % (reverse_lazy('admin:%s_%s_change' % (review.content_type.app_label, review.content_type.name), args=[item.object_id]),  item.object_id)
    cl.full_result_count = len(cl.result_list)
    cl.result_count = len(cl.result_list)

    #import pprint
    #pprint.pprint(vars(cl))
    res.context_data['review'] = review
    res.context_data['link_to_content_type'] = reverse_lazy('admin:%s_%s_changelist' % (review.content_type.app_label, review.content_type.model), args=[])
    return render_to_response('peerreview/items_list.html', res.context_data, context_instance = RequestContext(request))


def assign_selected_option(peer, items):
    for item in items:
        entries = list(item.entries.filter(peer = peer))
        if entries:
            setattr(item, 'selected_option_id', entries[0].selected_option.id)
            setattr(item, 'comments', entries[0].comment)
    return items

@login_required(login_url= reverse_lazy('peer-review-login'))
def details(request, review_id):
    review = Review.objects.select_related('option_group', 'content_type').get(id = review_id)
    template_name = '%s/%s_peerreview.html' % (review.content_type.app_label, review.content_type.name)

    restart_review = request.GET.get('restart_review', False)
    if restart_review:
        items_to_review = review.items.all()
    else:
        items_to_review = review.items.filter(~Q(entries__peer__in = (request.user,)))

    paginator = Paginator(items_to_review, review.pagination_count)

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    data = dict(
            restart_review = restart_review,
            review = review,
            items = assign_selected_option(request.user, items),
            review_options = review.option_group.options.all()
        )

    return smart_response(request, template_name, data)

    # Do we need app_name as well to be 100% sure?
@login_required(login_url= reverse_lazy('peer-review-login'))
def add_entry(request, review_id, content_type, content_id, review_option_id):
    actual_type = ContentType.objects.filter(model = content_type).distinct()[0]
    model_instance = actual_type.get_object_for_this_type(id = content_id)
    review = Review.objects.get(id = review_id)
    review_option = ReviewOption.objects.get(id = review_option_id)
    ReviewLogic.add_entry(review, model_instance, request.user, review_option)
    return HttpResponse('bar')


@login_required(login_url= reverse_lazy('peer-review-login'))
def add_items_to_review(request):
    selected_ids = [int(p) for p in request.POST.get('selected_ids').split(',')]
    content_type = request.POST.get('content_type')
    review = Review.objects.get(id = int(request.POST.get('review_id')))
    app_label = request.POST.get('app_label')
    actual_content_type = ContentType.objects.get(app_label=app_label, model=content_type)
    ReviewLogic.add_items(review, actual_content_type.model_class().objects.filter(id__in = selected_ids))
    return HttpResponseRedirect(request.POST.get('redirect_url'))
