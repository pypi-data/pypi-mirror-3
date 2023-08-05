from django.test import TransactionTestCase, Client

from contentmanager.models import *
from contentmanager.plugins import BasePlugin
from contentmanager import registry


class TestBasePlugin(BasePlugin):
    pass

registry.register(TestBasePlugin)


class ContentManagerModelTests(TransactionTestCase):
    fixtures = ["contentmanager_test"]

    def _get(self, pk):
        return Block.objects.get(pk=pk)

    def _get_order(self):
        return list(Block.objects.values_list('id',
                                              'position').order_by('position'))

    def test_save_and_delete_middle_position(self):
        b = self._get(pk=3)
        order = self._get_order()
        # create a new block in the middle
        Block(plugin_type=b.plugin_type, site=b.site, area=b.area, path=b.path,
              position=b.position).save()
        # check order
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (6, 2), (3, 3), (4, 4), (5, 5)])

        # delete it and check if previous order was restored
        self._get(pk=6).delete()
        self.assertEqual(self._get_order(), order)

    def test_save_and_delete_first_position(self):
        b = self._get(pk=1)
        order = self._get_order()
        # create a new block in the middle
        Block(plugin_type=b.plugin_type, site=b.site, area=b.area, path=b.path,
              position=b.position).save()
        # check order
        self.assertEqual(self._get_order(),
                         [(6, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])

        # delete it and check if previous order was restored
        self._get(pk=6).delete()
        self.assertEqual(self._get_order(), order)

    def test_save_and_delete_last_position(self):
        b = self._get(pk=5)
        order = self._get_order()
        # create a new block in the middle
        Block(plugin_type=b.plugin_type, site=b.site, area=b.area, path=b.path,
              position=b.position + 1).save()
        # check order
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5)])

        # delete it and check if previous order was restored
        self._get(pk=6).delete()
        self.assertEqual(self._get_order(), order)


class ContentManagerViewTests(TransactionTestCase):
    fixtures = ["contentmanager_test"]

    def _get(self, pk):
        return Block.objects.get(pk=pk)

    def _get_order(self):
        return list(Block.objects.values_list('id',
                                              'position').order_by('position'))

    def test_move_block(self):

        # login as admin
        c = Client()
        self.assertTrue(c.login(username='test', password='test'))

        # post down
        r = c.post('/contentmanager/3/move/',
                   {'direction': 'down'})

        # check response, should be redirect
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (4, 2), (3, 3), (5, 4)])

        # post up
        r = c.post('/contentmanager/3/move/',
                   {'direction': 'up'})

        # check response, should be redirect
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])


        # post invalid pk, no move and 404 status
        r = c.post('/contentmanager/999999/move/',
                   {'direction': 'up'})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])

        # post invalid direction, no move and 400 status
        r = c.post('/contentmanager/3/move/',
                   {'direction': 'INVALID MOVE'})

        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])

        # not logged in
        c.logout()
        r = c.post('/contentmanager/3/move/',
                   {'direction': 'up'})
        # redirect to login page
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])


class ManagerTests(TransactionTestCase):
    fixtures = ["contentmanager_test"]

    def _get(self, pk):
        return Block.objects.get(pk=pk)

    def _get_order(self):
        return list(Block.objects.values_list('id',
                                              'position').order_by('position'))

    def assertEqualQueryset(self, first, second, msg=None):
        for o in first:
            if o not in second:
                raise self.failureException, \
                      (msg or '%r != %r' % (first, second))
            for o in second:
                if o not in first:
                    raise self.failureException, \
                      (msg or '%r != %r' % (first, second))

    def test_get_sibblings(self):
        b = self._get(pk=3)
        a = Area.objects.get(pk=2)
        o = Block.objects.get_or_create(plugin_type=b.plugin_type,
                                        site=b.site, area=a, path=b.path,
                                        position=b.position)[0]

        self.assertEqual(Block.objects.get_sibblings(b).count(), 5)
        self.failIf(b not in Block.objects.get_sibblings(b))
        self.failIf(o in Block.objects.get_sibblings(b))
        self.assertEqual(Block.objects.get_sibblings(o).count(), 1)
        self.failIf(o not in Block.objects.get_sibblings(o))
        self.failIf(b in Block.objects.get_sibblings(o))

    def test_get_for_area_path(self):
        b = self._get(pk=3)
        self.assertEqualQueryset(Block.objects.get_for_area_path(b.area,
                                                                 b.path),
                                 Block.objects.get_sibblings(b))

    def test_move_down(self):
        pk = 3
        b = self._get(pk=pk)
        start_position = b.position

        # test move_down
        b = Block.objects.move_down(b)
        self.assertEqual(b.position, start_position + 1)
        self.assertEqual(self._get(pk=pk).position, b.position)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (4, 2), (3, 3), (5, 4)])

        # don't move if position is already highest
        while not b.is_last():
            b = Block.objects.move_down(b)
        b = Block.objects.move_down(b) # extra down
        self.assertEqual(b.position, 4)
        self.assertEqual(self._get(pk=pk).position, b.position)
        self.assertEqual(self._get_order(),
                         [(1, 0), (2, 1), (4, 2), (5, 3), (3, 4)])

    def test_move_up(self):
        pk = 3
        b = self._get(pk=pk)
        start_position = b.position

        # test move_up
        b = Block.objects.move_up(b)
        self.assertEqual(b.position, start_position - 1)
        self.assertEqual(self._get(pk=pk).position, b.position)
        self.assertEqual(self._get_order(),
                         [(1, 0), (3, 1), (2, 2), (4, 3), (5, 4)])

        # don't move if position is already 0
        while not b.is_first():
            b = Block.objects.move_up(b)
        b = Block.objects.move_up(b) # extra up
        self.assertEqual(b.position, 0)
        self.assertEqual(self._get(pk=pk).position, b.position)
        self.assertEqual(self._get_order(),
                         [(3, 0), (1, 1), (2, 2), (4, 3), (5, 4)])


class UtilsTests(TransactionTestCase):
    fixtures = ["contentmanager_test"]

    def test_get_area_ckey(self):
        from contentmanager.utils import get_area_ckey

        b = Block.objects.get(pk=1)
        # consistant ckey
        self.assertEqual(get_area_ckey(b.area, b.path),
                         get_area_ckey(b.area.pk, b.path.pk))
        self.assertEqual(get_area_ckey(b.area, b.path),
                         get_area_ckey(unicode(b.area), unicode(b.path)))
