from models import Block


# Don't die when haystack is not available
try:
    from haystack import site, indexes

    class BlockIndex(indexes.SearchIndex):
        text = indexes.CharField(document=True, use_template=True)

    site.register(Block, BlockIndex)

except ImportError:
    pass
