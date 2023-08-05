from django import forms

from contentmanager.models import Block, PluginType
from contentmanager import registry


def add_block_form_factory(request):
    """
    Creates a AddBlockForm class, based on request instance.

    """
    # Create an empty block to use below, it is never saved
    tmp_block = Block()
    plugin_type_ids = []
    for plugin_type, plugin_class in registry._registry.items():
        plugin = plugin_class(tmp_block)
        if request.user.is_superuser or \
                plugin.has_add_permission(request):
            plugin_type_ids.append(PluginType.objects.get_for_plugin_type(plugin_type).pk)

    queryset = PluginType.objects.filter(id__in=plugin_type_ids)

    properties = {
        'plugin_type': forms.ModelChoiceField(queryset.order_by("name")),
        'plugin_type_selected': forms.BooleanField(required=False,
                                                   initial=False ,
                                                   widget=forms.widgets.HiddenInput)
    }

    return type('AddBlockForm', (forms.Form,), properties)


class BlockEditForm(forms.ModelForm):

    class Meta:
        model = Block
        fields = ('klass', )
