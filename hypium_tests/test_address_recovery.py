from hypium import BY
from .do_support import DoCase


class NoAddressRecovery(DoCase):
    scenario = 'no-address'
    requirement_ids = ['E15', 'E16', 'E17', 'E18', 'E19', 'E20', 'E21', 'E23', 'E24', 'D02', 'D10']

    def test_missing_address_then_original_selection_and_retry(self):
        before = self.confirm_ready()
        self.assertIsNone(before['order']['selectedAddress'])
        self.submit()
        toast = self.require_component(BY.text('请选择收货地址'), 'Missing exact address Toast', timeout=2)
        self.assertEqual(toast.getText(), '请选择收货地址')
        bounds = toast.getBounds()
        (self.trace / 'toast-bounds.txt').write_text(str(bounds), encoding='utf-8')
        self.capture('missing-address-toast')
        self.assertEqual(self.creates(), [])
        actual = self.confirm_ready()
        self.assertNotIn('order/pay', actual['routeNames'])
        self.assertEqual(actual['carts'], before['carts'])
        self.click_key('order_confirm_address')
        self.click_key('address_select_907')
        returned = self.wait_state(lambda s: s.get('order') is not None and
                                   s['order']['selectedAddress'] is not None and
                                   s['order']['selectedAddress']['id'] == 907)
        self.assertEqual(returned['order']['cartList'], before['order']['cartList'])
        self.submit()
        self.wait_pay()
        self.assertEqual(self.creates()[0]['body']['data']['addressId'], 907)


class AddressCancel(DoCase):
    requirement_ids = ['D02', 'D03', 'D11']

    def test_original_address_back_preserves_current_draft(self):
        before = self.confirm_ready()
        self.input_key('order_confirm_remark_input', '保留备注')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.click_key('order_confirm_address')
        self.require_text('收货地址', 'Address list not visible')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        returned = self.confirm_ready()
        self.assertEqual(returned['order']['selectedAddress']['id'], 701)
        self.assertEqual(returned['order']['remark'], '保留备注')
        self.assertEqual(returned['order']['cartList'], before['order']['cartList'])
        self.assertEqual(self.creates(), [])


class NoAddressCancel(AddressCancel):
    scenario = 'no-address'

    def test_original_address_back_preserves_current_draft(self):
        before = self.confirm_ready()
        self.assertIsNone(before['order']['selectedAddress'])
        self.click_key('order_confirm_address')
        self.require_component(BY.key('address_list_page'), 'Original list not open')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        returned = self.confirm_ready()
        self.assertIsNone(returned['order']['selectedAddress'])
        self.assertEqual(returned['order']['cartList'], before['order']['cartList'])
        self.assertEqual(self.creates(), [])


class NewAddressRecovery(DoCase):
    scenario = 'no-address'
    server_options = {'empty_addresses': True}
    requirement_ids = ['E20', 'E22', 'E23', 'E24', 'D02']

    def test_original_add_refresh_select_and_submit(self):
        before = self.confirm_ready()
        self.click_key('order_confirm_address')
        self.require_component(BY.key('address_list_page'), 'Original empty address list not open')
        self.click_key('address_add_new')
        for key, text in [('address_contact_input', '本地新增丙'), ('address_phone_input', '13800000003'),
                          ('address_detail_input', '本地测试丙路1201号')]:
            self.driver.input_text(BY.key(key), text)
            self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        self.click_key('address_region_select')
        self.click_bottommost_exact_text('北京市')
        self.click_bottommost_exact_text('北京市')
        self.click_bottommost_exact_text('东城区')
        self.capture('complete-original-address-form')
        self.click_key('address_save')
        self.require_component(BY.key('address_select_1201'), 'Saved address absent after original list refresh')
        self.click_key('address_select_1201')
        returned = self.wait_state(lambda s: s.get('order') is not None and
                                   s['order']['selectedAddress'] is not None and
                                   s['order']['selectedAddress']['id'] == 1201)
        self.assertEqual(returned['order']['cartList'], before['order']['cartList'])
        self.submit()
        self.wait_pay()
        self.assertEqual(self.creates()[0]['body']['data']['addressId'], 1201)
        requests = self.control('state')['requests']
        self.assertEqual(sum(r['path'] == '/app/user/address/add' for r in requests), 1)
        self.assertGreaterEqual(sum(r['path'] == '/app/user/address/page' for r in requests), 2)


class AddressReplacement(DoCase):
    requirement_ids = ['E02', 'E03', 'E07', 'E08', 'E21', 'E23', 'E24', 'D01', 'D02', 'D03', 'D11']

    def test_nondefault_replaces_default_preserves_draft_and_submits(self):
        before = self.confirm_ready()
        self.assertEqual(before['order']['selectedAddress']['id'], 701)
        remark = '更换地址后保留中文备注'
        self.input_key('order_confirm_remark_input', remark)
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        entered = self.confirm_ready()
        self.assertEqual(entered['order']['remark'], remark)
        self.click_key('order_confirm_address')
        self.click_key('address_select_907')
        returned = self.wait_state(lambda s: s.get('order') is not None and
                                   s['order']['selectedAddress'] is not None and
                                   s['order']['selectedAddress']['id'] == 907)
        self.assertEqual(returned['order']['data']['defaultAddress']['id'], 701,
                         'Fixture default must remain701 while current selection becomes907')
        self.assertEqual(returned['order']['cartList'], before['order']['cartList'])
        self.assertEqual(returned['order']['selectedGoodsList'], before['order']['selectedGoodsList'])
        self.assertEqual(returned['order']['remark'], remark)
        self.visible_key('order_confirm_address')
        self.require_text('本地选择乙', 'Original confirmation UI did not show replacement contact')
        self.require_text('本地测试路907号', 'Original confirmation UI did not show replacement address')
        self.assertIsNone(self.find_or_none(BY.text('本地测试路701号'), timeout=0.5),
                          'Original confirmation UI still shows the old default address')
        self.assertIsNone(self.find_or_none(BY.text('本地默认甲'), timeout=0.5),
                          'Original confirmation UI still shows the old default contact')
        self.assertIsNone(self.find_or_none(BY.text('默认'), timeout=0.5),
                          'Nondefault selection must not retain the old default badge')
        self.capture('replacement-address-ui')
        self.visible_key('order_confirm_remark_input')
        self.require_text(remark, 'Original remark UI did not preserve Chinese text after selection')
        self.capture('replacement-remark-ui')
        self.click_key('order_confirm_address')
        self.require_component(BY.key('address_list_page'), 'Original list not open for cancellation')
        self.hdc('shell', 'uitest', 'uiInput', 'keyEvent', 'Back')
        cancelled = self.confirm_ready()
        self.assertEqual(cancelled['order']['selectedAddress']['id'], 907)
        self.assertEqual(cancelled['order']['cartList'], before['order']['cartList'])
        self.assertEqual(cancelled['order']['selectedGoodsList'], before['order']['selectedGoodsList'])
        self.assertEqual(cancelled['order']['remark'], remark)
        self.visible_key('order_confirm_address')
        self.require_text('本地测试路907号', 'Cancelling address selection lost the replacement UI')
        self.assertIsNone(self.find_or_none(BY.text('本地测试路701号'), timeout=0.5))
        self.capture('replacement-after-cancel-ui')
        self.assertEqual(self.creates(), [])
        self.submit()
        self.wait_pay()
        requests = self.creates()
        self.assertEqual(len(requests), 1)
        data = requests[0]['body']['data']
        self.assertEqual(data['addressId'], 907)
        self.assertEqual(data['remark'], remark)
        self.assertEqual(sorted((g['goodsId'], g['spec']['id'], g['count']) for g in data['goodsList']),
                         [(1701, 37, 1), (2903, 205, 3), (2903, 407, 2)])
