from django import template
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from featured.models import FeaturedItem

register = template.Library()

class GetFeaturedNode(template.Node):
    """
    Retrieves current featured item or default
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            item = FeaturedItem.published_objects.all().order_by('-published_date')[0]
        except:
            item = FeaturedItem.published_objects.get(default=True)

        context[self.varname] = item 
        return ''

def get_featured_item(parser, token):
    """
    Retrieves the current featured item, or the default

    {% get_featured_item as item %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as' 
    except AssertionError:
        raise template.TemplateSyntaxError('get_featured_item syntax: {% get_featured_item as varname %}')

    varname = None
    t, a, varname = args

    return GetFeaturedNode(varname=varname)

register.tag(get_featured_item)
