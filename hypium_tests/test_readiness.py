import time
from hypium import BY
from .do_support import DoCase


class DelayedConfirm(DoCase):
    server_options = {'confirm_delay': 3.0}
    requirement_ids = ['D11', 'D10']

    def test_delayed_get_never_creates_an_incomplete_order(self):
        submit = self.find_or_none(BY.key('order_confirm_submit'), timeout=0.25)
        if submit is not None:
            self.driver.click(submit)
        self.assertEqual(self.creates(), [])
        self.confirm_ready()
        self.submit()
        self.wait_pay()
        self.assertEqual(len(self.creates()), 1)


class ConfirmRetry(DoCase):
    server_options = {'confirm_fail_first': True}
    requirement_ids = ['D11', 'D10']

    def test_failed_get_retries_without_consuming_cached_goods_again(self):
        self.require_text('重新加载', 'Original GET retry not visible')
        self.assertEqual(self.creates(), [])
        self.driver.click(BY.text('重新加载'))
        ready = self.confirm_ready()
        self.assertEqual(sorted((g['goodsId'], g['spec']['id'], g['count']) for g in ready['order']['selectedGoodsList']),
                         [(1701, 37, 1), (2903, 205, 3), (2903, 407, 2)])
        self.submit()
        self.wait_pay()


class EmptyCache(DoCase):
    empty_cache = True
    requirement_ids = ['D11']

    def test_empty_cache_does_not_invent_an_order(self):
        self.wait_state(lambda s: s.get('order') is not None and s['order']['data'] is not None)
        submit = self.find_or_none(BY.key('order_confirm_submit'), timeout=0.5)
        if submit is not None:
            self.driver.click(submit)
        time.sleep(0.5)
        self.assertEqual(self.creates(), [])
        actual = self.wait_state(lambda s: s.get('order') is not None)
        self.assertEqual(actual['order']['selectedGoodsList'], [])
        self.assertNotIn('order/pay', actual['routeNames'])
