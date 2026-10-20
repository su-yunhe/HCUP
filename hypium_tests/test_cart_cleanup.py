import time
from hypium import BY
from .do_support import DoCase


class CartCleanup(DoCase):
    entry = 'cart'
    requirement_ids = ['E25', 'E26', 'E27', 'E28', 'E29', 'E30', 'E31', 'D01', 'D08']

    def test_original_cart_selection_cleanup_and_restart(self):
        self.click_key('main_tab_cart')
        for identifier in ('cart_select_1701_37', 'cart_select_2903_205', 'cart_select_2903_407'):
            self.click_key(identifier)
        self.click_key('cart_settle')
        self.confirm_ready()
        self.submit()
        self.wait_pay()

        def cleaned(s):
            carts = {c['goodsId']: c for c in s['carts']}
            return 2903 not in carts and 1701 in carts and {v['id'] for v in carts[1701]['spec']} == {11, 91}

        after = self.wait_state(cleaned)
        carts = {c['goodsId']: c for c in after['carts']}
        self.assertEqual([(s['id'], s['count']) for s in carts[1701]['spec']], [(11, 2), (91, 4)])
        self.assertEqual(carts[4109]['spec'][0]['id'], 4193)
        requests = self.creates()
        self.assertEqual(len(requests), 1)
        self.assertEqual(sorted((g['goodsId'], g['spec']['id'], g['count']) for g in requests[0]['body']['data']['goodsList']),
                         [(1701, 37, 1), (2903, 205, 3), (2903, 407, 2)])
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.click_key('main_tab_cart')
        self.require_component(BY.key('cart_spec_1701_11'), 'Cart UI did not refresh after original return')
        self.require_component(BY.key('cart_spec_1701_91'), 'Cart UI lost unpurchased spec')
        self.assertIsNone(self.find_or_none(BY.key('cart_goods_2903'), timeout=0.5))
        self.run_id += '-restart'
        self.start(preserve=True)
        restarted = self.wait_state(cleaned)
        self.assertEqual(restarted['carts'], after['carts'])
        self.assertEqual(len(self.creates()), 1)
        self.click_key('main_tab_cart')
        self.require_component(BY.key('cart_spec_1701_11'), 'Unpurchased spec missing after restart')
        self.require_component(BY.key('cart_spec_1701_91'), 'Unpurchased spec missing after restart')


class StaleSetCleanup(DoCase):
    entry = 'cart'
    requirement_ids = ['E28', 'E30', 'E31', 'D09']

    def test_same_count_different_current_and_purchased_sets(self):
        self.click_key('main_tab_cart')
        for identifier in ('cart_select_1701_11', 'cart_select_1701_91', 'cart_select_2903_205', 'cart_select_2903_407'):
            self.click_key(identifier)
        self.click_key('cart_settle')
        before = self.confirm_ready()
        self.assertEqual({g['spec']['id'] for g in before['order']['selectedGoodsList'] if g['goodsId'] == 1701}, {11, 91})
        self.click_key('do_stale_cart_seed')
        def changed(s):
            first = next((c for c in s['carts'] if c['goodsId'] == 1701), None)
            return first is not None and {v['id'] for v in first['spec']} == {11, 37}
        self.wait_state(changed)
        self.submit()
        self.wait_pay()
        def cleaned(s):
            carts = {c['goodsId']: c for c in s['carts']}
            return 2903 not in carts and 1701 in carts and {v['id'] for v in carts[1701]['spec']} == {37}
        after = self.wait_state(cleaned)
        self.assertEqual(next(c for c in after['carts'] if c['goodsId'] == 1701)['spec'][0]['count'], 1)
        self.assertTrue(any(c['goodsId'] == 4109 for c in after['carts']))
        self.assertEqual(len(self.creates()), 1)
