from django import http
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from contentmanager.models import Area, BlockPath, Block
from contentmanager.forms import add_block_form_factory, BlockEditForm
from contentmanager.utils import expire_cache
from contentmanager.registry import registry


@login_required
def _edit_block(request, block, base_template, caption="Edit"):
    """
    Common code for add and edit block
    """

    # This is injected into the forms (that don't already have a Media
    # attribute) below
    class Media:
        css = {
            'all': ('contentmanager/css/contentmanager.css',)
        }

    # remember this
    post_url = request.path

    # get plugin
    plugin = block.get_plugin()

    if caption=='Edit':
        has_perm = plugin.has_change_permission(request)
    else:
        has_perm = plugin.has_add_permission(request)

    # check permissions if needed
    if plugin.form and not has_perm:
        return http.HttpResponseBadRequest(
            _("Request was denied based on your permissions."))

    # form or not
    if plugin.form:
        form = plugin.get_form(request)
        if form.is_valid():
            # give plugin a chance to modify params dict
            block.params = plugin.pre_save_params(form)
        else:
            if not hasattr(form, 'Media'):
                # Inject the default contentmanager-styling
                form.Media = Media
            response = direct_to_template(request,
                                          'contentmanager/editblock.html',
                                          {"form": form,
                                           "help": plugin.help,
                                           "post_url": post_url,
                                           "plugin_name": plugin.plugin_type(),
                                           "plugin_type": block.plugin_type.pk,
                                           "cancel": block.path.path,
                                           "caption": caption,
                                           "template": base_template})
            if request.is_ajax():
                response['X-Contentmanager'] = 'showpluginform'
            return response
    else:
        # None editable has no params
        block.params = None

    # save changes
    block.save()

    # redirect
    if request.is_ajax():
        # return an empty page with a header to indicate the page
        # should be redirected otherwise the redirect has to take
        # place twice (and worse, the page has to be rendered twice)
        return http.HttpResponse('', 'text/plain')
    return http.HttpResponseRedirect(block.get_absolute_url())

@login_required
def add_block(request, area_id, path_id, position):
    """
    """
    area = get_object_or_404(Area, pk=area_id)
    path = get_object_or_404(BlockPath, pk=path_id)

    # remember this
    post_url = request.path

    # set template to extend
    if request.is_ajax():
        base_template = 'contentmanager/ajax.html'
    else:
        base_template = 'contentmanager/base.html'

    AddBlockForm = add_block_form_factory(request)

    if request.POST: # and step = 0
        form = AddBlockForm(request.POST)
        if form.is_valid():
            # check block in registry
            plugin_type = form.cleaned_data["plugin_type"]
            if not registry.is_registered(plugin_type.name):
                return http.HttpResponseBadRequest(_("Request wasn't valid."))

            # create block initial block
            block = Block(plugin_type=plugin_type, area=area, path=path,
                          position=position)

            # get plugin
            plugin = block.get_plugin()

            # check permissions
            if not plugin.has_add_permission(request):
                return http.HttpResponseBadRequest(
                    _("Request was denied based on your permissions."))

            # we need to reset request.POST
            if not form.cleaned_data["plugin_type_selected"]:
                request.POST = {}

            # same as edit
            return _edit_block(request, block, base_template, "Add")
    else:
        # show plugin options
        form = AddBlockForm()

    return direct_to_template(request,
                              'contentmanager/listblocktypes.html',
                              {"form": form,
                               "post_url": post_url,
                               "cancel": path.path,
                               "template": base_template})


@login_required
def edit_block(request, block_id):
    """
    """
    # set template to extend
    if request.is_ajax():
        base_template = 'contentmanager/ajax.html'
    else:
        base_template = 'contentmanager/base.html'

    # get block
    block = get_object_or_404(Block, pk=block_id)

    # common code base
    return _edit_block(request, block, base_template)

@login_required
def style_block(request, block_id):
    if request.is_ajax():
        base_template = 'contentmanager/ajax.html'
    else:
        base_template = 'contentmanager/base.html'

    # get block
    block = get_object_or_404(Block, pk=block_id)

    # check permissions
    if not block.get_plugin().has_change_permission(request):
        return http.HttpResponseBadRequest(
            _("Request was denied based on your permissions."))

    if request.POST:
        form = BlockEditForm(request.POST, instance=block)
        if form.is_valid():
            redirect_to = block.get_absolute_url()
            form.save()
            if request.is_ajax():
                return http.HttpResponse('', 'text/plain')
            return http.HttpResponseRedirect(redirect_to)
    else:
        form = BlockEditForm(instance=block)
    return direct_to_template(request,
                              'contentmanager/style.html',
                              {'blck': block, 
                               'form': form,
                               'template': base_template})


@login_required
def delete_block(request, block_id):
    """
    User can only delete block if they have delete permissions
    """
    if request.is_ajax():
        base_template = 'contentmanager/ajax.html'
    else:
        base_template = 'contentmanager/base.html'

    # get block
    block = get_object_or_404(Block, pk=block_id)

    # check permissions
    if not block.get_plugin().has_delete_permission(request):
        return http.HttpResponseBadRequest(
            _("Request was denied based on your permissions."))

    if request.POST:
        # check confirm and delete if needed.
        if request.POST.get('confirm', '') == _('Yes'):
            redirect_to = block.get_absolute_url()
            block.delete()
            return http.HttpResponseRedirect(redirect_to)
    else:
        return direct_to_template(request,
                                  'contentmanager/confirmdelete.html',
                                  {'blck': block, 'template': base_template})

@login_required
@require_POST
def move_block(request, block_id):
    """
    User can only move block if they have add permission.

    If we would handle this in the same way as delete it would be easier to
    if request is still valid. using etags/last_modified
    """

    # get block
    block = get_object_or_404(Block, pk=block_id)

    # check permissions
    if not block.get_plugin().has_add_permission(request):
        return http.HttpResponseBadRequest(
            _("Request was denied based on your permissions."))

    # direction
    direction = request.POST.get("direction", 'INVALID')

    if direction == 'up':
        block = Block.objects.move_up(block)
    elif direction == 'down':
        block = Block.objects.move_down(block)
    else:
        return http.HttpResponseBadRequest(_("Request wasn't valid."))

    expire_cache(block.area, block.path)
    return http.HttpResponseRedirect(block.get_absolute_url())
