from hypium import BY
from .do_support import DoCase


class FaultCartBase(DoCase):
    entry = 'cart'
    fault_required = True

    def original_cart_checkout(self):
        self.click_key('main_tab_cart')
        for identifier in ('cart_select_1701_37', 'cart_select_2903_205', 'cart_select_2903_407'):
            self.click_key(identifier)
        self.click_key('cart_settle')
        ready = self.confirm_ready()
        self.assertTrue(ready['faultBoundaryInstalled'], 'Not the approved fault sandbox')
        return ready


class DelayedCleanup(FaultCartBase):
    fault_mode = 'delete-delay'
    requirement_ids = ['E27', 'E28', 'D06']

    def test_payment_precedes_delayed_real_database_deletion(self):
        before = self.original_cart_checkout()
        self.submit()
        pay = self.wait_pay()
        self.assertEqual(pay['carts'], before['carts'], 'Pay was blocked on the bounded 8s database boundary')
        def cleaned(s):
            carts = {c['goodsId']: c for c in s['carts']}
            return 2903 not in carts and {v['id'] for v in carts[1701]['spec']} == {11, 91}
        cleaned_state = self.wait_state(cleaned, timeout=25)
        raw = (self.trace / 'actual-hilog.log').read_text(encoding='utf-8')
        import re
        allowed_times = [int(v) for v in re.findall(r'HCUP_DO_BOUNDARY\] DELETE_IO_ALLOWED (\d+)', raw)]
        self.assertTrue(allowed_times, 'No actual fault-boundary timeline')
        self.assertLess(pay['observedAt'], min(allowed_times), 'Pay route must be observed before deletion I/O is released')
        self.assertEqual(len(self.creates()), 1)


class FailedCleanup(FaultCartBase):
    fault_mode = 'fail-1701'
    requirement_ids = ['D06', 'U05_ADOPTED_POLICY']

    def test_one_database_failure_does_not_stop_other_goods_or_recreate(self):
        before = self.original_cart_checkout()
        self.submit()
        self.wait_pay()
        after = self.wait_state(lambda s: not any(c['goodsId'] == 2903 for c in s['carts']))
        first = lambda s: next(c for c in s['carts'] if c['goodsId'] == 1701)
        self.assertEqual(first(after), first(before), 'The deliberately failed item must remain in DB')
        self.assertEqual(len(self.creates()), 1)
        # The failed item remaining is expected in this fault test, never E28 full-clean pass.


class DelayedCache(DoCase):
    fault_required = True
    fault_mode = 'cache-delay'
    requirement_ids = ['D11', 'D10']

    def test_delayed_cache_prevents_incomplete_http_order(self):
        button = self.find_or_none(BY.key('order_confirm_submit'), timeout=0.25)
        if button is not None:
            self.driver.click(button)
        self.assertEqual(self.creates(), [])
        ready = self.confirm_ready()
        self.assertTrue(ready['faultBoundaryInstalled'])
        self.submit()
        self.wait_pay()
        self.assertEqual(len(self.creates()), 1)
