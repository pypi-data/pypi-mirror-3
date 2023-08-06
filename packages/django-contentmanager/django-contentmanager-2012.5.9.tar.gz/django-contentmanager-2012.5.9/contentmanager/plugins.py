

# following example from django/contrib/auth/management/__init__.py
def _get_permission_codename(plugin, action):
    from plugins import BasePlugin
    if isinstance(plugin, BasePlugin):
        name = plugin.__class__.__name__
    else:
        name = plugin.__name__
    return u'%s_%s_plugin' % (action, name.lower())


def _get_all_permissions(plugin):
    "Returns (codename, name) for all permissions in this plugin."
    perms = []
    for action in ('add', 'change', 'delete'):
        perms.append((_get_permission_codename(plugin, action),
                      u'Can %s %s plugin' % (action, plugin.verbose_name)))
    return perms + list(plugin.permissions)


def create_permissions(plugin):
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    from contentmanager.models import PluginType
    ctype = ContentType.objects.get_for_model(PluginType)
    for codename, name in _get_all_permissions(plugin):
        p, created = Permission.objects.get_or_create(
            codename=codename, content_type__pk=ctype.id,
            defaults={'name': name, 'content_type': ctype})


class BasePlugin(object):
    """
    Base for plugins
    """
    form = None
    help = None
    cacheable = True
    verbose_name = None
    verbose_name_plural = None
    permissions = ()

    def __init__(self, block):
        self.block = block
        self.opts = self.block._meta

    @classmethod
    def plugin_type(cls):
        """
        This is the identifier of your plugin.

        WARNING: changing this value will destroy the link with db data.
        """
        if cls.verbose_name:
            return cls.verbose_name
        else:
            return cls.__name__

    def get_form(self, request):
        """
        Return form instance to be used.
        """
        if self.form is None:
            return None
        if request.POST:
            return self.form(request.POST, request.FILES)
        return self.form(initial=self.params)

    def render(self, request):
        """
        This should return the content when plugin is shown.
        """
        from django.utils.translation import ugettext as _
        raise NotImplemented(_(u"render needs to be implemented"))

    @property
    def params(self):
        """
        Return params or empty dictionary.
        """
        if self.block.params:
            return self.block.params
        return {}

    def pre_save_params(self, form):
        """
        Should return a pickleable dictionary or None
        """
        return form.cleaned_data

    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an block.
        """
        return request.user.has_perm(
            "%s.%s" % ('contentmanager',
                       _get_permission_codename(self, "add")))

    def has_change_permission(self, request):
        """
        Returns True if the given request has permission to change the given
        block instance.
        """
        return request.user.has_perm(
            "%s.%s" % ('contentmanager',
                       _get_permission_codename(self, "change")))

    def has_delete_permission(self, request):
        """
        Returns True if the given request has permission to delete the given
        block instance.
        """
        return request.user.has_perm(
            "%s.%s" % ('contentmanager',
                       _get_permission_codename(self, "delete")))

    def get_perms(self, request):
        """
        Returns a dict of all perms for this block. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            }


class BaseModelPlugin(BasePlugin):
    """
    This can be used if a plugin correlates with a model

    This use by default the model permissions and also it's verbose names.
    """
    model = None

    def __init__(self, *args, **kwargs):
        super(BaseModelPlugin, self).__init__(*args, **kwargs)
        self.opts = self.model._meta
        if self.verbose_name is None:
            self.verbose_name = self.opts.verbose_name
        if self.verbose_name_plural is None:
            self.verbose_name_plural = self.opts.verbose_name_plural

    def get_obj(self):
        pk = self.params.get("pk", None)
        if pk:
            try:
                return self.model.objects.get(pk=pk)
            except self.model.DoesNotExist:
                return None
        return None

    def pre_save_params(self, form):
        obj = form.save()
        return {"pk": obj.pk}

    def get_form(self, request):
        instance = self.get_obj()
        if request.POST:
            return self.form(request.POST, request.FILES, instance=instance)
        return self.form(instance=instance)

    def delete(self):
        """
        Allow (model)plugins to clean up if they so chose.

        The default behaviour is to *not* delete the objects from the
        model
        """
        pass

    def render(self, request):
        """ Generic plugin rendering

        """
        from django.template.loader import render_to_string
        from django.template import RequestContext

        obj = self.get_obj()
        if not obj:
            return "%s no longer exists." % (self.verbose_name)
        objname = self.__class__.__name__.lower()
        return render_to_string('%s/%s.html' % (self.opts.app_label, objname),
                                {objname: obj},
                                context_instance=RequestContext(request))
