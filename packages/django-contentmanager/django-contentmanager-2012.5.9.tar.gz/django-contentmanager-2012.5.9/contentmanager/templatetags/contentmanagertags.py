from django import template
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest
from django.template import TemplateSyntaxError

from contentmanager import registry
from contentmanager.registry import NotRegistered
from contentmanager.models import Block, BlockPath, Area
from contentmanager.utils import get_area_ckey


register = template.Library()


class AreaNode(template.Node):
    """

    """

    def __init__(self, request, area, path=None, small=False):
        self.request = template.Variable(request)
        self.area = template.Variable(area)
        self.small = small
        if path is not None:
            self.path = template.Variable(path)
        else:
            self.path = None

    def render(self, context):
        request = self.request.resolve(context)
        area = self.area.resolve(context)

        # path not set use request.path
        if self.path is not None:
            path = self.path.resolve(context)
        else:
            path = request.path

        # get path and area objects
        area = Area.objects.get_for_area(area)
        path = BlockPath.objects.get_for_path(path)

        # get cache key
        ckey = get_area_ckey(area, path)

        # Never cache in editmode

        if 'editmode' in request.GET:
            # Don't update session if no change has been made.
            current = request.session.get('contentmanager_editmode', False)
            if request.GET['editmode'] == '1' and not current \
               and request.user.is_authenticated():
                request.session['contentmanager_editmode'] = True
            elif request.GET['editmode'] == '0' and current:
                request.session['contentmanager_editmode'] = False
        elif not request.user.is_authenticated():
            request.session['contentmanager_editmode'] = False


        editmode = request.session.get('contentmanager_editmode', False)
        if editmode:
            content = None
            templatename = 'contentmanager/contentmanager.html'
        else:
            content = cache.get(ckey)
            # only used when there's no content in the cache
            templatename = 'contentmanager/content.html'

        # if the cache has content we exit now
        if content:
            return content

        # get blocks
        blocks = Block.objects.get_for_area_path(area,
                                                 path).order_by('position')

        # check if we can cache and create plugins
        can_cache = True
        for blck in blocks:
            # A single uncacheble block prevents the entire area from
            # being cached...
            if not registry.cacheable(unicode(blck.plugin_type)):
                can_cache = False

        # render content
        context = template.RequestContext(request, {'blocks': blocks,
                                                    'area': area,
                                                    'small': self.small,
                                                    'path': path})
        
        content = template.loader.render_to_string(templatename, context)

        # store the area's content in cache... except when not
        if can_cache and not editmode:
            cache.set(ckey, content)
        elif not can_cache:
            # this might be needed if a plugin has changed his cacheable.
            cache.delete(ckey)
        return content


@register.tag
def get_area(parser, token):
    """
    Render all plugins in a area, with optional fixed path.

    {% get_area <request> <area> <small>%}
    {% get_area <request> <area> for <path> <small> %}
    """
    bits = token.split_contents()
    small = False
    if len(bits) in [4,6]:
        small = str(bits.pop()).lower() == "small"
    if len(bits) != 3 and len(bits) != 5:
        raise template.TemplateSyntaxError(
            "incorrect get_area format")

    if len(bits) == 5:
        if bits[3] != 'for':
            raise template.TemplateSyntaxError(
                "third argument to the get_area tag must be 'for'")
        return AreaNode(bits[1], bits[2], bits[4], small)
    return AreaNode(bits[1], bits[2], small=small)


class BlockNode(template.Node):

    def __init__(self, request, block):
        self.request = template.Variable(request)
        self.block = template.Variable(block)

    def render(self, context):
        try:
            request = self.request.resolve(context)
        except template.VariableDoesNotExist:
            # This is here mostly for haystack/whoosh
            request = HttpRequest()
            request.user = AnonymousUser()
        block = self.block.resolve(context)

        # get plugin
        try:
            plugin = block.get_plugin()
        except NotRegistered, error:
            from django.conf import settings
            if settings.DEBUG:
                return repr(error)
            else:
                return ''
        # render
        try:
            return plugin.render(request)
        except Exception, error:
            from django.conf import settings
            if settings.DEBUG:
                return repr(error)
            else:
                return "<!-- plugin '" + \
                    plugin.verbose_name + "' failed to render -->"

@register.tag
def render_block(parser, token):
    """
    {% render_block request block %}
    """
    bits = token.split_contents()

    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "render_block tag takes exactly two argument")

    return BlockNode(bits[1], bits[2])
