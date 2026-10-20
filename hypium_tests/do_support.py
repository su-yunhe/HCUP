from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import time
import unittest
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from harness.driver import HarnessTestCase
from hypium import BY

ROOT = Path('D:/HCUP/cml-spec17')
spec = importlib.util.spec_from_file_location('do_evidence', ROOT / 'workflow/do-entry/evidence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DoCase(HarnessTestCase):
    device_sn = '127.0.0.1:11243'
    bundle = 'com.hcup.cmlspec17.localdo'
    scenario = 'with-address'
    entry = 'confirm'
    server_mode = 'success'
    server_options = {}
    fault_mode = ''
    empty_cache = False
    fault_required = False
    requirement_ids = []

    @classmethod
    def setUpClass(cls):
        if os.environ.get('HCUP_DO_RUN_AUTHORIZED') != '1':
            raise unittest.SkipTest('Device run not authorized; scaffold only')
        if cls.fault_required and os.environ.get('HCUP_DO_VARIANT') != 'fault':
            raise unittest.SkipTest('This test requires the separately identified fault sandbox')
        if cls.device_sn != '127.0.0.1:11243':
            raise RuntimeError('Refusing a different task device')
        super().setUpClass()
        cls.driver.set_implicit_wait_time(0)

    def setUp(self):
        self.run_id = self._testMethodName + '-' + uuid.uuid4().hex[:10]
        round_name = os.environ.get('HCUP_DO_ROUND', 'do-01')
        if not __import__('re').fullmatch(r'do-\d{2}(-fault)?', round_name):
            raise RuntimeError('Invalid owned test round')
        self.trace = ROOT / 'traces' / round_name / 'runtime' / self.run_id
        self.trace.mkdir(parents=True)
        self.last_probe_time = 0
        self.configure_server(scenario=self.scenario, mode=self.server_mode, **self.server_options)
        self.start()

    def configure_server(self, **values):
        self.control('reset', dict(run_id=self.run_id, **values))

    def control(self, operation, value=None):
        data = json.dumps(value, ensure_ascii=False).encode() if value is not None else None
        request = urllib.request.Request(f'http://127.0.0.1:18173/_control/{operation}', data=data,
                                         headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.load(response)

    def hdc(self, *values):
        command = ['hdc', '-t', self.device_sn, *map(str, values)]
        completed = subprocess.run(command, capture_output=True, encoding='utf-8', errors='replace', timeout=30)
        record = dict(utc=datetime.now(timezone.utc).isoformat(), command=command, exit_code=completed.returncode,
                      stdout=completed.stdout, stderr=completed.stderr)
        with (self.trace / 'commands.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
        if completed.returncode or '[Fail]' in completed.stdout:
            raise RuntimeError(record)
        return completed.stdout

    def start(self, preserve=False, empty_addresses=False):
        self.hdc('shell', 'aa', 'force-stop', self.bundle)
        values = ['shell', 'aa', 'start', '-a', 'EntryAbility', '-b', self.bundle,
                  '--ps', 'hcupDoScenario', self.scenario, '--ps', 'hcupDoEntry', self.entry,
                  '--ps', 'hcupDoRun', self.run_id]
        if preserve:
            values += ['--ps', 'hcupDoPreserve', 'yes']
        if empty_addresses:
            values += ['--ps', 'hcupDoAddressList', 'empty']
        if self.fault_mode:
            values += ['--ps', 'hcupDoFault', self.fault_mode]
        if self.empty_cache:
            values += ['--ps', 'hcupDoCache', 'empty']
        self.hdc(*values)

    def visible_key(self, key):
        target = self.find_or_none(BY.key(key), timeout=1.0)
        if target is not None:
            return target
        # ArkUI lazily omits off-screen Scroll/List children. Use actual original
        # container swipes; no VM assignments and no weakened business assertion.
        upward_first = key in ('order_confirm_address', 'address_contact_input', 'address_phone_input')
        directions = [False, True] if upward_first else [True, False]
        for toward_end in directions:
            for _ in range(5):
                y1, y2 = (2250, 900) if toward_end else (950, 2200)
                self.hdc('shell', 'uitest', 'uiInput', 'swipe', 650, y1, 650, y2, 1400)
                target = self.driver.find_component(BY.key(key))
                if target is not None:
                    return target
        self.fail(f'Missing original UI id {key} after bounded original-container scrolling')

    def click_key(self, key):
        target = self.visible_key(key)
        self.driver.click(target)

    def input_key(self, key, text, clear=False):
        self.visible_key(key)
        if clear:
            self.driver.clear_text(BY.key(key))
        if text:
            self.driver.input_text(BY.key(key), text)

    def click_bottommost_exact_text(self, text):
        time.sleep(0.4)
        self.require_text(text, f'Missing original selectable text {text}')
        matches = [v for v in self.driver.find_all_components(BY.text(text)) if v.getText() == text]
        self.assertTrue(matches)
        bounds = [v.getBounds() for v in matches]
        current = max(bounds, key=lambda v: v.top)
        self.driver.click(((current.left + current.right) // 2, (current.top + current.bottom) // 2))
        time.sleep(0.4)

    def wait_state(self, predicate, timeout=15):
        deadline = time.monotonic() + timeout
        last, incomplete = None, []
        while time.monotonic() < deadline:
            # A parent @Entry component can stop its timer after navigation.
            # Explicit read-only diagnostics avoid treating a retained old VM
            # snapshot as the current route/DB. Never invokes a business action.
            if time.monotonic() - self.last_probe_time >= 1.0:
                probe = self.driver.find_component(BY.key('do_probe_dump'))
                if probe is not None:
                    self.driver.click(probe)
                    self.last_probe_time = time.monotonic()
                    time.sleep(0.15)
            pid = self.hdc('shell', 'pidof', self.bundle).strip()
            if pid:
                raw = self.hdc('shell', 'hilog', '-x', '-P', pid)
                (self.trace / 'actual-hilog.log').write_text(raw, encoding='utf-8')
                states, incomplete = module.states_from_hilog(raw, self.run_id)
                if states:
                    last = states[-1]
                    (self.trace / 'actual-state.json').write_text(json.dumps(last, ensure_ascii=False, indent=2), encoding='utf-8')
                    (self.trace / 'incomplete-chunks.json').write_text(json.dumps(incomplete), encoding='utf-8')
                    if predicate(last):
                        return last
            time.sleep(0.25)
        self.fail(f'Actual state not reached; last={last}; incomplete={incomplete}')

    def confirm_ready(self):
        return self.wait_state(lambda s: s.get('order') is not None and bool(s['order']['cartList'])
                               and s['order']['data'] is not None)

    def creates(self):
        state = self.control('state')
        (self.trace / 'http-state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        return [r for r in state['requests'] if r['method'] == 'POST' and r['path'] == '/app/order/info/create']

    def submit(self):
        self.click_key('order_confirm_submit')

    def assert_no_payment_or_cart_change(self, before):
        actual = self.confirm_ready()
        self.assertNotIn('order/pay', actual['routeNames'])
        self.assertEqual(actual['carts'], before['carts'])
        return actual

    def wait_pay(self, real_price=4321, identifier=83017):
        actual = self.wait_state(lambda s: bool(s['routeNames']) and s['routeNames'][-1] == 'order/pay')
        params = json.loads(actual['payParamsJson'])
        self.assertEqual(len(params), 1, 'Expected one actual pay route')
        self.assertEqual(params[0]['orderId'], identifier)
        self.assertEqual(params[0]['price'], real_price)
        self.require_text('订单支付', 'Original payment page not visible')
        return actual

    def capture(self, label):
        for suffix, action in [('png', 'screenCap'), ('json', 'dumpLayout')]:
            remote = f'/data/local/tmp/cml17-do-{label}.{suffix}'
            self.hdc('shell', 'uitest', action, '-p', remote)
            destination = self.trace / f'{label}.{suffix}'
            self.hdc('file', 'recv', remote, destination)
            self.assertGreater(destination.stat().st_size, 0)

    def tearDown(self):
        self.capture('final')
        self.creates()
        (self.trace / 'requirement-map.json').write_text(json.dumps(self.requirement_ids), encoding='utf-8')
