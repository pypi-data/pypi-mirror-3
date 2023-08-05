from django.core.cache import cache
from django.conf import settings


def get_area_ckey(area, path):
    """
    Get area key based on current site, area and path

    area and path can be there respected object, pk or string.
    """
    from models import Area, BlockPath

    if isinstance(area, int):
        pass
    elif isinstance(area, Area):
        area = area.pk
    else:
        area = Area.objects.get_for_area(area).pk

    if isinstance(path, int):
        pass
    elif isinstance(path, BlockPath):
        path = path.pk
    else:
        path = BlockPath.objects.get_for_path(path).pk

    return u'contentmanager:%d:%d:%d' % (settings.SITE_ID, area, path)


def expire_cache(area, path):
    """
    Expires the cache for current site, area/path combination.
    """
    cache.delete(get_area_ckey(area, path))
