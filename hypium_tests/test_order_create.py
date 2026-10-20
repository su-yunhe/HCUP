"""Run only after the production manifest/HAP/serial run gate is approved."""
import time

from hypium import BY
from .do_support import DoCase


class OrderSuccess(DoCase):
    requirement_ids = ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08', 'E09',
                       'E10', 'E11', 'E12', 'E13', 'E14', 'D01', 'D07']

    def test_original_submit_actual_http_and_response_parameters(self):
        before = self.confirm_ready()
        self.assertEqual(before['order']['selectedAddress']['id'], 701)
        self.require_component(BY.key('order_confirm_goods_1701'), 'Selected goods1701 not shown in original page')
        self.require_component(BY.key('order_confirm_goods_2903'), 'Selected goods2903 not shown in original page')
        self.capture('original-confirm-ready')
        self.input_key('order_confirm_remark_input', '请轻放，周末送达')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        coupon_row = self.visible_key('order_confirm_coupon').getBounds()
        self.hdc('shell', 'uitest', 'uiInput', 'click', (coupon_row.left + coupon_row.right) // 2,
                 (coupon_row.top + coupon_row.bottom) // 2)
        time.sleep(0.6)
        self.capture('coupon-sheet-open')
        # A diagnostic banner tap outside an open modal would dismiss it.
        # Wait on the original sheet UI, then read the VM after selecting.
        self.require_component(BY.key('order_coupon_item_503'), 'Original coupon503 row absent', timeout=5)
        time.sleep(0.4)
        choice = self.require_component(BY.key('order_coupon_item_503'), 'Original coupon503 row absent').getBounds()
        self.hdc('shell', 'uitest', 'uiInput', 'click', (choice.left + choice.right) // 2,
                 (choice.top + choice.bottom) // 2)
        time.sleep(0.4)
        self.capture('coupon-selected-ui')
        self.wait_state(lambda s: s.get('order') is not None and s['order']['selectedCoupon'] is not None and
                        s['order']['selectedCoupon']['id'] == 503 and not s['order']['couponModalVisible'])
        self.submit()
        after = self.wait_pay()
        requests = self.creates()
        self.assertEqual(len(requests), 1)
        data = requests[0]['body']['data']
        self.assertEqual(data['addressId'], 701)
        self.assertEqual(data['remark'], '请轻放，周末送达')
        self.assertEqual(data['couponId'], 503)
        self.assertEqual(sorted((g['goodsId'], g['spec']['id'], g['count']) for g in data['goodsList']),
                         [(1701, 37, 1), (2903, 205, 3), (2903, 407, 2)])
        self.assertEqual(after['carts'], before['carts'], 'Direct purchase must not clean the cart')

    def test_completed_draft_active_submit_reuses_receipt(self):
        self.confirm_ready()
        self.submit()
        self.wait_pay()
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.confirm_ready()
        self.assertEqual(len(self.creates()), 1)
        self.submit()
        self.wait_pay()
        self.assertEqual(len(self.creates()), 1)


class ZeroPayment(DoCase):
    server_mode = 'zero'
    requirement_ids = ['E10', 'E11', 'E12', 'E13', 'E14']

    def test_zero_real_payment_is_valid(self):
        self.confirm_ready()
        self.submit()
        self.wait_pay(real_price=0)
        self.assertEqual(len(self.creates()), 1)


class SlowSubmission(DoCase):
    server_mode = 'slow'
    server_options = {'delay': 3.0}
    requirement_ids = ['D05', 'D10']

    def test_inflight_repeated_clicks_create_once(self):
        before = self.confirm_ready()
        submit = self.require_component(BY.key('order_confirm_submit'), 'Original submit missing')
        bounds = submit.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        for _ in range(5):
            self.driver.click(point)
        pending = self.wait_state(lambda s: bool(s['routeNames']) and s['routeNames'][-1] == 'order/confirm')
        self.assertEqual(pending['carts'], before['carts'])
        self.wait_pay()
        self.assertEqual(len(self.creates()), 1)


class FailureRetry(DoCase):
    server_mode = 'failure-then-success'
    requirement_ids = ['D04', 'D05', 'D10']

    def test_business_failure_does_not_clean_and_can_retry(self):
        before = self.confirm_ready()
        self.submit()
        deadline = time.monotonic() + 5
        while not self.creates() and time.monotonic() < deadline:
            time.sleep(0.1)
        time.sleep(1)
        actual = self.confirm_ready()
        self.assertEqual(actual['carts'], before['carts'])
        self.assertNotIn('order/pay', actual['routeNames'])
        self.submit()
        self.wait_pay(identifier=83018)
        self.assertEqual(len(self.creates()), 2)


class InvalidResponses(DoCase):
    requirement_ids = ['D04', 'D10']

    def check_invalid(self, mode, settle=1.0):
        self.configure_server(scenario=self.scenario, mode=mode)
        before = self.confirm_ready()
        self.submit()
        deadline = time.monotonic() + 5
        while not self.creates() and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertEqual(len(self.creates()), 1)
        time.sleep(settle)
        self.assert_no_payment_or_cart_change(before)
        self.configure_server(scenario=self.scenario, mode='success')
        self.submit()
        self.wait_pay()
        self.assertEqual(len(self.creates()), 1)

    def test_success_null_data_is_not_an_order(self):
        self.check_invalid('null')

    def test_success_missing_id_is_not_an_order(self):
        self.check_invalid('missing-id')

    def test_success_missing_real_price_is_not_zero_price(self):
        self.check_invalid('missing-price')

    def test_negative_real_price_is_rejected_by_adopted_policy(self):
        self.check_invalid('negative-price')

    def test_http_failure_releases_submission(self):
        self.check_invalid('http-failure')

    def test_actual_socket_timeout_does_not_clean_or_navigate(self):
        self.check_invalid('timeout', settle=11)


class RemarkValues(DoCase):
    requirement_ids = ['E02', 'E08', 'D07']

    def check_remark(self, value):
        self.confirm_ready()
        self.input_key('order_confirm_remark_input', value, clear=True)
        if value:
            self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.submit()
        self.wait_pay()
        data = self.creates()[0]['body']['data']
        self.assertEqual(data.get('remark'), value)
        self.assertIsNone(data.get('couponId'))

    def test_empty_remark_without_coupon_is_accepted(self):
        self.check_remark('')

    def test_three_spaces_are_preserved_by_adopted_policy(self):
        self.check_remark('   ')
