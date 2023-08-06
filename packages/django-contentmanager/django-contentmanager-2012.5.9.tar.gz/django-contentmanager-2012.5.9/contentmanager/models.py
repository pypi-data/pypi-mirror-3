from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site

from contentmanager.managers import *
from contentmanager.fields import PickledObjectField
from contentmanager.utils import expire_cache
from contentmanager import registry


try:
    KLASS_CHOICES = settings.CONTENT_MANAGER_KLASSES
except AttributeError:
    KLASS_CHOICES = None


class Area(models.Model):
    """
    Indicates where plugins/blocks should be loaded in a template.
    """
    name = models.CharField(_("name"), max_length=255)
    site = models.ForeignKey(Site, related_name="areas",
                             default=settings.SITE_ID)
    description = models.TextField(_("description"), blank=True)

    objects = AreaManager()

    class Meta:
        verbose_name = _("area")
        verbose_name_plural = _("areas")
        unique_together = ("name", "site")

    def __unicode__(self):
        return self.name


class PluginType(models.Model):
    """
    This holds all the registrated plugin types.
    """
    name = models.CharField(_("name"), max_length=255, unique=True)

    objects = PluginTypeManager()

    class Meta:
        verbose_name = _("plugin type")
        verbose_name_plural = _("plugin types")

    def __unicode__(self):
        return self.name


class BlockPath(models.Model):
    """
    Path where block is located.
    """
    path = models.CharField(_("path"), max_length=255)
    site = models.ForeignKey(Site, related_name="blockpaths",
                             default=settings.SITE_ID)

    objects = BlockPathManager()

    class Meta:
        verbose_name = _("block path")
        verbose_name_plural = _("block paths")
        unique_together = ('path', 'site')

    def __unicode__(self):
        return self.path


class Block(models.Model):
    """
    Store plugin_type, location and data
    """
    # type
    plugin_type = models.ForeignKey(PluginType, related_name="blocks")
    # location
    site = models.ForeignKey(Site, related_name="blocks",
                             default=settings.SITE_ID)
    area = models.ForeignKey(Area, related_name="blocks")
    path = models.ForeignKey(BlockPath, related_name="blocks")
    position = models.PositiveSmallIntegerField(_("position"), db_index=True)
    # data
    klass = models.CharField(_("class"), max_length=250, blank=True,
                             choices=KLASS_CHOICES)
    params = PickledObjectField(editable=False, null=True, blank=True)
    # meta data
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(db_index=True, editable=False)

    objects = BlockManager()

    class Meta:
        verbose_name = _("block")
        verbose_name_plural = _("blocks")
        # until deffered unique constraint are in postgres 8.5
        #unique_together = ("site", "area", "path", "position")

    def save(self, *args, **kwargs):
        """
        Allow creation of a block in any position.
        """
        if not self.id:
            self.created = datetime.now()
            # make space for this block.
            Block.objects.filter(
                area=self.area,
                path=self.path,
                position__gte=self.position
            ).update(position=models.F('position') + 1)
        self.updated = datetime.now()
        super(Block, self).save(*args, **kwargs)
        # clear cache
        expire_cache(self.area, self.path)

    def delete(self, *args, **kwargs):
        """
        Clean up database positions after delete.
        """
        area = self.area
        path = self.path
        position = self.position
        super(Block, self).delete(*args, **kwargs)
        # condense space left behind.
        Block.objects.filter(
            area=area,
            path=path,
            position__gt=position
        ).update(position=models.F('position') - 1)
        # clear cache
        expire_cache(area, path)

    def __unicode__(self):
        return u"[%s]%s position:%s" % (self.area, self.path, self.position)

    def get_absolute_url(self, anchor_pattern="#block_%(id)s"):
        return unicode(self.path) + (anchor_pattern % self.__dict__)

    def is_first(self):
        """
        Checks if current block has first position
        """
        return self.position == 0

    def is_last(self):
        """
        Checks if current block has last position
        """
        qs = Block.objects.get_sibblings(self)
        result = qs.aggregate(models.Max('position'))
        return self.position == result["position__max"]

    def get_plugin_class(self):
        """
        Returns associated Plugin class from register.
        """
        return registry.get_plugin(self.plugin_type.name)

    def get_plugin(self):
        """
        Returns a plugin instance for this block.
        """
        if not hasattr(self, "_plugin"):
            klass = self.get_plugin_class()
            self._plugin = klass(self)
        return self._plugin

    def editable(self):
        """
        Indicates if the plugin has a form and is (therefor) editable
        """
        klass = self.get_plugin_class()
        return klass.form is not None
