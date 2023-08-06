from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template import Library, Node
from django import template
from django.contrib.contenttypes.models import ContentType

from peerreview.models import ReviewEntry

#from django.core.context_processors import csrf
#context = RequestContext(request)
#context.update(csrf(request))

register = template.Library()

@register.simple_tag
def review_item_head_script():
    result = """
    <script type="text/javascript">
        function review_item(item_id, option_id, comments){
            $.post('%s', { item_id: item_id, option_id: option_id, csrfmiddlewaretoken: '{{csrf_token}}', comments: comments } );
        }
    </script>
    """ % (reverse('peer-review-review-item'), )
    return mark_safe(result)


#@register.inclusion_tag('comments.html')
#def display_comments(document_id):
#    document = models.Document.objects.get(id__exact=document_id)
#    comments = models.Comment.objects.filter(document=document)[0:5]
#    return { 'comments': comments }

# in template comments.html:
#{% for comment in comments %}<blockquote>{{ comment.text }}</blockquote>{% endfor %}


#<li><a href="/login/user/{{ object_id }}?hash={{ 'user'|hash:object_id }}">Login</a></li>
#https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
#@register.filter()
#def hash(type, id):
#    hash = hashlib.md5()
#    hash.update("%s:%s:%s" % (type, id, settings.ADMIN_HASH_SECRET))
#    return hash.hexdigest().upper()
#
##<p>This post was last updated at {% format_time blog_entry.date_updated "%Y-%m-%d %I:%M %p" %}.</p>
#
#def do_format_time(parser, token):
#    try:
#        # split_contents() knows not to split quoted strings.
#        tag_name, date_to_be_formatted, format_string = token.split_contents()
#    except ValueError:
#        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
#    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
#        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
#    return FormatTimeNode(date_to_be_formatted, format_string[1:-1])
#
#class FormatTimeNode(template.Node):
#    def __init__(self, date_to_be_formatted, format_string):
#        self.date_to_be_formatted = template.Variable(date_to_be_formatted)
#        self.format_string = format_string
#
#    def render(self, context):
#        try:
#            actual_date = self.date_to_be_formatted.resolve(context)
#            return actual_date.strftime(self.format_string)
#        except template.VariableDoesNotExist:
#            return ''

class ReviewEntriesNode(Node):
    def __init__(self, instance):
        self.instance = template.Variable(instance)

    def render(self, context):
        #print context.keys()
        actual_instance = self.instance.resolve(context)
        content_type = ContentType.objects.get_for_model(actual_instance)
        print ReviewEntry.objects.select_related().filter(item__content = actual_instance)
        context['review_entries'] = ReviewEntry.objects.select_related().filter(item__content_type = content_type, item__object_id = actual_instance.id)
        return ''

def get_review_entries(parser, token):
    tag_name, instance = token.split_contents()[0:2]
    return ReviewEntriesNode(instance)

get_review_entries = register.tag(get_review_entries)

#class ReviewNode(Node):
#    def __init__(self, review):
#        self.review = template.Variable(review)
#
#    def render(self, context):
#        actual_review = self.review.resolve(context)
#        context['review_entries'] = ReviewEntry.objects.select_related().filter(item__content_type = content_type, item__object_id = actual_instance.id)
#        return ''
#
#def get_review_entries(parser, token):
#    tag_name, instance = token.split_contents()[0:2]
#    return ReviewEntriesNode(instance)
#
#get_review_entries = register.tag(get_review_entries)


@register.inclusion_tag('peerreview/frontend/review_item.html')
def review_item(review, section):
    return dict(
        review=review,
        not_started = section == 'not_started',
        started = section == 'started',
        finished = section == 'finished'
    )