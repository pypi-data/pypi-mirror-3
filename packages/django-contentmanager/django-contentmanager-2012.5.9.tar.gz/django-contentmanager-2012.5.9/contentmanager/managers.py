from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import models, transaction

from django.contrib.sites.managers import CurrentSiteManager


class AreaManager(CurrentSiteManager):

    def get_for_area(self, name, force=False):
        """
        Returns the area object for a given name, creating the area
        if necessary. Lookups are cached so that subsequent lookups
        for the same name don't hit the database.
        """
        key = "AreaManager:%s:get_for_area:%s" % (settings.SITE_ID, name)
        a = cache.get(key)
        if a is None or force:
            a, created = self.get_or_create(name=name)
            cache.set(key, a)
        return a


class PluginTypeManager(models.Manager):

    def get_for_plugin_type(self, plugin_type, force=False):
        """
        Returns the plugin_type object for a given plugin_type string, creating
        the plugin_type if necessary. Lookups are cached so that subsequent
        lookups for the same plugin_type don't hit the database.
        """
        plugin_type_cache_name = "".join(plugin_type.split())
        key = "PluginTypeManager:get_by_plugin_type:%s" % plugin_type_cache_name
        a = cache.get(key)
        if a is None or force:
            a, created = self.get_or_create(name=plugin_type)
            cache.set(key, a)
        return a


class BlockPathManager(CurrentSiteManager):

    def get_for_path(self, path, force=False):
        """
        Returns the blockpath object for a given path, creating the area
        if necessary. Lookups are cached so that subsequent lookups
        for the same path don't hit the database.
        """

        key = "BlockPathManager:%s:get_for_path:%s" % (settings.SITE_ID, path)
        a = cache.get(key)
        if a is None or force:
            a, created = self.get_or_create(path=path)
            cache.set(key, a)
        return a


class BlockManager(CurrentSiteManager):
    """
    Uses CurrentSiteManager as base extend from there.
    """

    def get_query_set(self):
        """
        Always get the related objects, as we use them quite often.
        """
        qs = super(BlockManager, self).get_query_set()
        return qs.select_related(depth=1)

    def get_for_area_path(self, area, path):
        """
        Returns blocks on the same site, area and path.
        """
        return self.get_query_set().filter(path=path,
                                           area=area).order_by("position")

    def get_sibblings(self, block):
        """
        Returns blocks on the same site, area and path for a block.
        """
        assert isinstance(block, self.model)
        return self.get_for_area_path(block.area, block.path)

    @transaction.commit_on_success
    def move_up(self, block):
        """
        Move block one postion up

        Use returning block instance, else futhur saves may fail.
        """
        assert isinstance(block, self.model)
        if not block.is_first():
            qs = self.get_sibblings(block)
            now = datetime.now()

            # shuffle
            qs.filter(position__gte=block.position - 1).update(position=models.F('position') + 1, updated=now)
            self.get_query_set().filter(pk=block.pk).update(position=models.F('position') - 2, updated=now)
            qs.filter(position__gt=block.position).update(position=models.F('position') - 1, updated=now)

            # update position of current object, else future save will fail.
            block.position = block.position - 1
            block.updated = now
        return block

    @transaction.commit_on_success
    def move_down(self, block):
        """
        Move block one postion down

        Use returning block instance, else futhur saves may fail.
        """
        assert isinstance(block, self.model)
        if not block.is_last():
            qs = self.get_sibblings(block)
            now = datetime.now()

            # shuffle order
            qs.filter(position__gt=block.position + 1).update(position=models.F('position') + 1, updated=now)
            self.get_query_set().filter(pk=block.pk).update(position=models.F('position') + 2, updated=now)
            qs.filter(position__gte=block.position).update(position=models.F('position') - 1, updated=now)

            # update position of current object, else future saves might fail.
            block.position = block.position + 1
            block.updated = now
        return block
