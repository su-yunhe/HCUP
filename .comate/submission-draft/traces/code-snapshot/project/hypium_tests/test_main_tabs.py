"""Eight device flows covering approved cml-spec1 A1-A44.

Run after installing the current HAP using the ordinary common runner:
  python -m harness.runner --project ... --device <serial> --json ...
The parent Agent coordinates source freeze and device ownership for this run.
Original device PNGs, UI trees and engine snapshots are all retained.
"""
from __future__ import annotations

import json
import hashlib
import os
import time
from pathlib import Path

import cv2
import numpy as np
from hypium import BY
from harness.driver import HarnessTestCase

from .evidence import (ROOT, KEYS, LABELS, Evidence, FrameCapture, ObservationUnavailable, area, intersection,
                       rectangle, save_json, shape_variants, still_metrics)


class MainTabsTests(HarnessTestCase):
    bundle = "com.joker.coolmall"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver.set_implicit_wait_time(.1)
        run_id = os.environ.get("CML_RUN_ID", time.strftime("run-%Y%m%d-%H%M%S"))
        cls.run_dir = ROOT / "traces" / "verification-do-r1" / run_id
        cls.run_dir.mkdir(parents=True, exist_ok=True)
        cls.first_frame_references = {}
        resources = ROOT / "feature/main/src/main/resources/rawfile/lottie"
        cls.duration = 0
        for key in KEYS:
            data = json.loads((resources / f"tab_{key}.json").read_text(encoding="utf-8-sig"))
            cls.duration = max(cls.duration, (float(data["op"]) - float(data["ip"])) / float(data["fr"]))
        if not 0 < cls.duration <= 15:
            raise AssertionError(f"Invalid/unbounded local Lottie duration: {cls.duration}")
        save_json(cls.run_dir / "run-context.json", {"device": cls.device_sn, "resourceDuration": cls.duration,
                                                   "pythonSource": str(Path(__file__)), "started": time.time(),
                                                   "testSourceSHA256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                                                        for p in (Path(__file__), Path(__file__).with_name("evidence.py"))},
                                                   "emptyInput": "N/A: Spec has no text input/submission",
                                                   "whitespaceInput": "N/A: Spec has no text input/submission"})

    def setUp(self):
        self.e = Evidence(self, self.device_sn, self.run_dir)
        self.finished = False
        self.receive_anchor = None
        self.offscreen_observation = 0

    def tearDown(self):
        try:
            self.e.snapshot("final" if self.finished else "failure")
        finally:
            save_json(self.e.path / "case-result.json", {"completed": self.finished,
                                                        "test": self._testMethodName,
                                                        "observations": self.e.observations})
            self.e.unchanged()

    def wait_for(self, predicate, message, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(.1)
        raise AssertionError(message)

    def ready(self):
        return self.e.component("main_root", required=False) is not None

    def launch(self, capture=False):
        previous = self.e.cmd("shell", "pidof", self.bundle, check=False)
        self.driver.stop_app(self.bundle, wait_time=.5)
        empty_samples = 0
        stopped = []
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            result = self.e.cmd("shell", "pidof", self.bundle, check=False)
            value = result.stdout.strip()
            if value and not all(part.isdigit() for part in value.split()):
                raise ObservationUnavailable(f"Cannot confirm stopped bundle process: {value}")
            stopped.append({"time": time.monotonic(), "pids": value})
            empty_samples = empty_samples + 1 if not value else 0
            if empty_samples >= 3:
                break
            time.sleep(.2)
        if empty_samples < 3:
            raise ObservationUnavailable("Old bundle did not reach a reliable fully stopped state; do not issue start")
        time.sleep(.5)
        save_json(self.e.path / f"cold-stop-{self.e.seq}.json",
                  {"beforePid": previous.stdout.strip(), "samples": stopped, "continuousEmpty": empty_samples,
                   "settledSecondsAfterConfirmation": .5, "policy": "One normal start only; no failure retry"})
        if capture:
            trace = self.observe("initial", lambda: self.driver.start_app(self.bundle, page_name="EntryAbility", wait_time=0))
        else:
            self.driver.start_app(self.bundle, page_name="EntryAbility", wait_time=0)
            trace = None
        self.wait_for(self.ready, "Normal application entry did not expose main_root (record system window/permission blocker)")
        self.wait_idle()
        return trace

    def wait_idle(self, key=None):
        def idle():
            if not self.ready():
                return False
            root = self.e.state("main_root")
            target = key or KEYS[int(root["selectedIndex"])]
            state = self.e.state(f"main_tab_{target}_icon", required=False)
            if state is None:
                return False
            if state.get("error"):
                raise AssertionError(f"Real Lottie error: {state['error']}")
            return state.get("ready") and state.get("paused")
        self.wait_for(idle, f"Lottie did not reach a real finite paused state: {key}", timeout=max(15, self.duration * 4))

    def tap(self, key):
        self.driver.click(self.e.component(f"main_tab_{key}"))

    def swipe(self, direction):
        self.driver.swipe(direction, distance=65, area=BY.key("main_content_pager"), swipe_time=.35)

    def observe(self, label, action, seconds=None):
        self.e.seq += 1
        label = f"{self.e.seq:02}_{label}"
        before = self.e.sample(all_icons=True)
        state_start = len(self.e.states)
        capture = FrameCapture(self.e, label).start()
        start = time.monotonic()
        states = []
        error = None
        try:
            action()
            action_done = time.monotonic()
            end = action_done + (seconds if seconds is not None else max(4.4, self.duration * 2 + .8))
            while time.monotonic() < end:
                states.append(self.e.sample())
                time.sleep(.08)
        except BaseException as exc:
            error = exc
            action_done = time.monotonic()
        finally:
            capture.finish()
        final = self.e.sample(all_icons=True)
        nodes = self.e.snapshot(label + "_settled")
        trace = {"label": label, "before": before, "states": self.e.states[state_start:], "final": final, "nodes": nodes,
                 "actionStart": start, "actionEnd": action_done, "capture": capture}
        save_json(capture.path / "action-and-engine.json", {k: v for k, v in trace.items() if k != "capture"})
        if error:
            raise error
        return trace

    def assert_current(self, key, nodes=None):
        root = self.e.state("main_root")
        index = KEYS.index(key)
        self.assertEqual(root["selectedIndex"], index, "Committed content index must match the selected tab")
        pager = self.e.state("main_content_pager")
        self.assertEqual(pager["selectedIndex"], index, "Pager and root must have the same actual committed page")
        for other in KEYS:
            selected = self.e.state(f"main_tab_{other}")["selected"]
            self.assertEqual(selected, other == key, f"Exactly one tab must be selected: {other}")
        nodes = nodes or self.e.tree(f"current_{self.e.seq}_{key}")
        p = self.node(nodes, "main_content_pager")["attributes"]
        page = self.node(nodes, f"{key}_page")["attributes"]
        viewport = rectangle(p["bounds"])
        page_bounds = rectangle(page.get("origBounds", page["bounds"]))
        self.assertGreater(intersection(viewport, page_bounds) / max(1, area(viewport)), .65,
                           "Preconstructed node existence cannot replace visible current content")
        bar = rectangle(self.node(nodes, "main_tab_bar")["attributes"]["bounds"])
        self.assertLessEqual(viewport[3], bar[1] + 4, "Fixed tab bar must be below the content viewport")
        return root

    def node(self, nodes, ident):
        entries = nodes.get(ident, [])
        self.assertEqual(len(entries), 1, f"Stable ID must be unique in the actual tree: {ident}")
        return entries[0]

    def bounds(self, nodes, key):
        return rectangle(self.node(nodes, f"main_tab_{key}_icon")["attributes"]["bounds"])

    def assert_play(self, trace, key, exactly_once=True):
        states = [r[key] for r in trace["states"] if key in r]
        final = trace["final"][key]
        self.assertTrue(final["ready"], "Actual Lottie DOM must be ready")
        self.assertFalse(final.get("error"), f"Actual Lottie engine error: {final.get('error')}")
        self.assertTrue(final["paused"], "Selected animation must finish its finite playback")
        self.assertGreater(final["frame"], 0, "Actual engine frame must advance, not stay a static first frame")
        self.assertTrue(any(float(s["frame"]) > 0 for s in states), "No actual forward engine frame sampled")
        before = trace["before"].get(key)
        if exactly_once and before is not None:
            self.assertEqual(final["observedPlaySeq"] - before["observedPlaySeq"], 1,
                             "A real selection must produce exactly one new observed playback sequence")
            self.assertEqual(final["completeSeq"] - before["completeSeq"], 1,
                             "A real selection must complete exactly one finite playback")
        sequences = {s["observedPlaySeq"] for s in states if s.get("observedPlaySeq", 0) > (before or {}).get("observedPlaySeq", 0)}
        self.assertEqual(len(sequences), 1, "Multiple real playback sequences occurred for one action")
        samples = trace["capture"].roi(self.bounds(trace["nodes"], key), key, after=trace["actionStart"])
        if "root" not in trace["before"]:
            # Cold launch may contain launcher/transition pixels at the eventual icon
            # coordinates. Require an unchanged inactive neighbor to prove that the
            # actual app tab bar was visible before counting home shape variants.
            neighbor = "category" if key == "home" else "home"
            anchor_bounds = self.bounds(trace["nodes"], neighbor)
            settled = cv2.imread(str(self.e.path / f"{trace['label']}_settled.png"))
            x1, y1, x2, y2 = anchor_bounds
            reference = settled[y1:y2, x1:x2].astype(np.int16)
            anchors = trace["capture"].roi(anchor_bounds, "app-visible-anchor", after=trace["actionStart"])
            visible_indices = set()
            for timing, image in anchors:
                delta = np.max(np.abs(image.astype(np.int16) - reference), axis=2)
                if float(delta.mean()) <= 2 and float((delta > 10).mean()) <= .05:
                    visible_indices.add(timing["index"])
            samples = [(timing, image) for timing, image in samples if timing["index"] in visible_indices]
            save_json(trace["capture"].path / "cold-app-visible-samples.json",
                      {"inactiveNeighbor": neighbor, "indices": sorted(visible_indices),
                       "purpose": "Exclude launcher/fade frames from actual app Lottie proof"})
        variants, distances = shape_variants(samples)
        save_json(trace["capture"].path / f"dynamic-{key}.json",
                  {"sampleCount": len(samples), "shapeVariants": variants, "silhouetteDifferences": distances})
        self.assertGreaterEqual(len(samples), 3, "Playback needs at least three real timed ROI samples")
        gaps = [b[0]["hostMonotonic"] - a[0]["hostMonotonic"] for a, b in zip(samples, samples[1:])]
        if variants < 3 and (not gaps or max(gaps) > self.duration / 3):
            raise ObservationUnavailable("Screenshot throughput missed the real animation window; improve capture and rerun rather than lower the animation requirement")
        self.assertGreaterEqual(variants, 3, "Actual icon silhouette did not change: counters/color alone do not prove Lottie")
        return samples

    def assert_still(self, trace, key, reset=False, compare_sequence=True):
        final = trace["final"][key]
        self.assertTrue(final["ready"] and final["paused"], f"{key} is not a ready paused real engine")
        if reset:
            self.assertAlmostEqual(float(final["frame"]), 0, delta=.05, msg="Inactive engine must actually reset to first frame")
        samples = trace["capture"].roi(self.bounds(trace["nodes"], key), f"still-{key}",
                                         after=trace["actionEnd"] + .5)
        metrics = still_metrics(samples)
        save_json(trace["capture"].path / f"still-{key}.json", {"frame": final["frame"], "metrics": metrics})
        for item in metrics:
            self.assertLessEqual(item["meanDelta"], .5, "Actual paused icon ROI continued changing")
            self.assertLessEqual(item["changedFractionOver5"], .01, "Actual paused icon shape was not stable")
        if reset:
            first = samples[0][1]
            if key not in self.first_frame_references:
                self.first_frame_references[key] = first.copy()
                cv2.imwrite(str(self.run_dir / f"first-frame-reference-{key}.png"), first)
                save_json(self.run_dir / f"first-frame-reference-{key}.json",
                          {"provenance": str(trace["capture"].path), "actualEngineFrame": final["frame"],
                           "paused": final["paused"], "scope": "Real engine goToAndStop(0), actual gray ROI; not a fabricated render"})
            reference = self.first_frame_references[key]
            self.assertEqual(first.shape, reference.shape, "First-frame observation geometry changed")
            delta = np.max(np.abs(first.astype(np.int16) - reference.astype(np.int16)), axis=2)
            self.assertLessEqual(float(delta.mean()), .5, "Reset ROI differs from the same actual gray first-frame reference")
        before = trace["before"].get(key)
        if before is not None and compare_sequence:
            self.assertEqual(final["observedPlaySeq"], before["observedPlaySeq"], "Unexpected new playback while inactive/same tab")

    def assert_colors(self, trace, selected):
        image = cv2.imread(str(self.e.path / f"{trace['label']}_settled.png"))
        metrics = {}
        for key in KEYS:
            x1, y1, x2, y2 = self.bounds(trace["nodes"], key)
            roi = image[y1:y2, x1:x2]
            channels = roi.astype(np.int16)
            neutral = channels.max(2) - channels.min(2) <= 8
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            foreground = gray[neutral & (gray < 220)]
            self.assertGreater(len(foreground), 20, f"No visible rendered icon pixels: {key}")
            value = float(np.median(foreground))
            metrics[key] = {"neutralForegroundPixels": len(foreground), "medianLuminance": value}
            if key == selected:
                self.assertLessEqual(value, 20, "Selected icon must be black")
            else:
                self.assertGreaterEqual(value, 116, "Inactive icon must be the approved neutral gray")
                self.assertLessEqual(value, 140, "Inactive icon must be the approved neutral gray")
        save_json(trace["capture"].path / "color-metrics.json", metrics)

    def receive_visible(self, nodes):
        entries = nodes.get("home_coupon_receive", [])
        if not entries:
            self.assertIsNotNone(self.receive_anchor, "Offscreen absence requires a previously visible, verified same coupon anchor")
            offset = self.y()
            self.assertGreater(offset, 1, "Missing anchor is not proof of scrolling without a real nonzero offset")
            self.assertEqual(self.e.state("main_root")["selectedIndex"], 0,
                             "Anchor absence on another page cannot establish home scroll invisibility")
            self.offscreen_observation += 1
            proof = f"offscreen-coupon-{self.offscreen_observation}"
            image = self.e.screenshot(proof)
            save_json(self.e.path / f"{proof}.json", {"initialAnchor": self.receive_anchor,
                      "actualYOffset": offset, "screenshot": str(image),
                      "interpretation": "SDK omitted fully clipped node; actual scroll and original screenshot support invisibility"})
            return False
        attrs = self.node(nodes, "home_coupon_receive")["attributes"]
        self.assertEqual(attrs.get("text"), "领取", "Top coupon anchor must keep exact Spec text")
        box = rectangle(attrs.get("origBounds", attrs["bounds"]))
        scroll = rectangle(self.node(nodes, "home_scroll")["attributes"]["bounds"])
        pager = rectangle(self.node(nodes, "main_content_pager")["attributes"]["bounds"])
        viewport = [max(scroll[0], pager[0]), max(scroll[1], pager[1]), min(scroll[2], pager[2]), min(scroll[3], pager[3])]
        visible = attrs.get("visible", "true") != "false" and intersection(box, viewport) / max(1, area(box)) > .8
        if visible:
            if self.receive_anchor is None:
                self.receive_anchor = {"stableId": "home_coupon_receive", "text": attrs["text"],
                                       "accessibilityId": attrs.get("accessibilityId"), "bounds": box,
                                       "instanceId": self.e.state("main_root")["instanceId"]}
                save_json(self.e.path / "initial-coupon-anchor.json", self.receive_anchor)
            else:
                self.assertEqual(self.e.state("main_root")["instanceId"], self.receive_anchor["instanceId"])
                self.assertEqual(attrs.get("accessibilityId"), self.receive_anchor["accessibilityId"],
                                 "Return-to-top must show the same real coupon node, not a replacement")
        return visible

    def y(self):
        return float(self.e.state("home_scroll")["yOffset"])

    def scroll_down(self):
        before = self.y()
        if self.receive_anchor is None:
            origin = self.e.tree(f"scroll_origin_{self.e.seq}")
            self.e.screenshot(f"scroll_origin_{self.e.seq}")
            self.assertTrue(self.receive_visible(origin), "Verify the original top coupon before creating an offscreen precondition")
        for n in range(6):
            self.driver.swipe("UP", distance=55, area=BY.key("home_scroll"), swipe_time=.45)
            time.sleep(.2)
            nodes = self.e.tree(f"scroll_{self.e.seq}_{n}")
            if not self.receive_visible(nodes):
                self.assertGreater(self.y(), before + 1, "Anchor must leave viewport through real nonzero scrolling")
                return nodes
        raise AssertionError("Could not move the same top coupon anchor outside the real scroll viewport")

    def visible_text(self, text):
        component = self.require_text(text, f"Expected actual local empty/unlogged state: {text}")
        box = rectangle(component.getBounds())
        viewport = rectangle(self.e.component("main_content_pager").getBounds())
        self.assertGreater(intersection(box, viewport) / max(1, area(box)), .8, f"Text exists but is not visible: {text}")
        self.e.log({"assertVisibleText": text, "bounds": box, "pagerBounds": viewport, "time": time.monotonic()})

    def test_01_scene_one_click_navigation(self):
        self.launch()
        nodes = self.e.snapshot("home_initial")
        with self.e.check("A1"):
            for key, label in zip(KEYS, LABELS):
                self.e.component(f"main_tab_{key}")
                attrs = self.node(nodes, f"main_tab_{key}_text")["attributes"]
                self.assertEqual(attrs["text"], label)
                self.assertGreater(area(rectangle(attrs["bounds"])), 0)
        with self.e.check("A2", "A3"):
            self.assert_current("home", nodes)
        trace = self.observe("click_category", lambda: self.tap("category"))
        with self.e.check("A4"):
            self.assert_current("category", trace["nodes"])
        with self.e.check("A5"):
            self.assert_play(trace, "category")
        with self.e.check("A6", "A7"):
            self.assert_colors(trace, "category")
        trace = self.observe("click_cart", lambda: self.tap("cart"))
        with self.e.check("A8"):
            self.assert_current("cart", trace["nodes"])
        with self.e.check("A9"):
            self.assert_play(trace, "cart")
        self.finished = True

    def test_02_scene_two_swipe_then_click(self):
        self.launch()
        trace = self.observe("home_left_category", lambda: self.swipe("LEFT"))
        with self.e.check("A10", "A11"):
            self.assert_current("category", trace["nodes"])
        with self.e.check("A12"):
            self.assert_play(trace, "category")
        trace = self.observe("category_left_cart", lambda: self.swipe("LEFT"))
        with self.e.check("A13", "A29"):
            self.assert_current("cart", trace["nodes"])
            self.assert_play(trace, "cart")
        trace = self.observe("cart_click_me", lambda: self.tap("me"))
        with self.e.check("A14"):
            self.assert_current("me", trace["nodes"])
        with self.e.check("A15"):
            self.assert_play(trace, "me")
        self.finished = True

    def test_03_scene_three_initial_reset_return(self):
        trace = self.launch(capture=True)
        with self.e.check("A16"):
            self.assert_current("home", trace["nodes"])
            self.assert_play(trace, "home")
        trace = self.observe("home_click_me", lambda: self.tap("me"))
        with self.e.check("A17"):
            self.assert_current("me", trace["nodes"])
        with self.e.check("A18"):
            self.assert_play(trace, "me")
        with self.e.check("A19"):
            self.assert_still(trace, "home", reset=True)
        trace = self.observe("me_return_home", lambda: self.tap("home"))
        with self.e.check("A20"):
            self.assert_play(trace, "home")
        with self.e.check("A21"):
            self.assert_current("home", trace["nodes"])
        with self.e.check("A22"):
            attrs = self.node(trace["nodes"], "main_tab_home_text")
            color = str(attrs.get("extraAttrs", {}).get("FontColor", ""))
            image = cv2.imread(str(self.e.path / f"{trace['label']}_settled.png"))
            x1, y1, x2, y2 = rectangle(attrs["attributes"]["bounds"])
            roi = image[y1:y2, x1:x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            ink = gray[gray < 220]
            self.assertGreater(len(ink), 20, "Home label needs visible glyph pixels")
            self.assertLessEqual(float(np.median(ink)), 20, "Home label must actually render black, separately from icon")
            if color:
                self.assertRegex(color, r"(?i)#(?:ff)?000000", "Observed text FontColor is not black")
            save_json(trace["capture"].path / "home-text-color.json",
                      {"FontColor": color or "not exposed by SDK XML; image evidence used", "bounds": [x1, y1, x2, y2],
                       "glyphPixels": int(len(ink)), "medianLuminance": float(np.median(ink))})
        self.finished = True

    def test_04_scene_four_scroll_and_reselect(self):
        self.launch()
        nodes = self.e.snapshot("coupon_at_top")
        self.assertTrue(self.receive_visible(nodes), "Scene four requires the real top coupon entry before scrolling")
        nodes = self.scroll_down()
        with self.e.check("A23", "A34"):
            self.assert_current("home", nodes)
            self.assertFalse(self.receive_visible(nodes))
            self.assertGreater(self.y(), 1)
        old_y = self.y()
        self.observe("leave_scrolled_home", lambda: self.tap("me"))
        returned = self.observe("return_preserve_scroll", lambda: self.tap("home"))
        with self.e.check("A44"):
            self.assert_current("home", returned["nodes"])
            self.assertAlmostEqual(self.y(), old_y, delta=2, msg="Cross-tab return must preserve actual home offset")
            self.assert_play(returned, "home")
            self.assertFalse(self.receive_visible(returned["nodes"]))
        instance = returned["final"]["root"]["instanceId"]
        trace = self.observe("selected_home_scroll_to_top", lambda: self.tap("home"))
        with self.e.check("A24", "A25"):
            self.assertAlmostEqual(self.y(), 0, delta=1)
            self.assertTrue(self.receive_visible(trace["nodes"]))
        with self.e.check("A26", "A27"):
            self.assert_current("home", trace["nodes"])
            for sample in [trace["before"], *trace["states"], trace["final"]]:
                self.assertEqual(sample["root"]["selectedIndex"], 0)
                self.assertEqual(sample["root"]["selectionEpoch"], trace["before"]["root"]["selectionEpoch"])
                self.assertEqual(sample["root"]["instanceId"], instance)
        with self.e.check("A28"):
            self.assert_still(trace, "home")
        self.finished = True

    def test_05_bidirectional_and_endpoint_policies(self):
        self.launch()
        # Includes every non-boundary neighbor direction and every selected icon.
        for direction, target in [("LEFT", "category"), ("LEFT", "cart"), ("LEFT", "me"),
                                  ("RIGHT", "cart"), ("RIGHT", "category"), ("RIGHT", "home")]:
            trace = self.observe(f"neighbor_{direction}_{target}", lambda d=direction: self.swipe(d))
            with self.e.check("A29", "A30", "A43"):
                self.assert_current(target, trace["nodes"])
                self.assert_play(trace, target)
                self.assert_colors(trace, target)
                for inactive in KEYS:
                    if inactive != target:
                        self.assert_still(trace, inactive, reset=True)
        for target, direction in [("home", "RIGHT"), ("me", "LEFT")]:
            if target != "home":
                self.observe("go_me_endpoint", lambda: self.tap(target))
            trace = self.observe(f"endpoint_{target}", lambda d=direction: self.swipe(d))
            with self.e.check("A40"):
                self.assert_current(target, trace["nodes"])
                self.assertEqual(trace["final"]["root"]["selectionEpoch"], trace["before"]["root"]["selectionEpoch"])
                self.assert_still(trace, target)
        for target in ("category", "cart", "me"):
            self.observe(f"go_{target}_before_reclick", lambda k=target: self.tap(k))
            trace = self.observe(f"reclick_{target}", lambda k=target: self.tap(k))
            with self.e.check("A41"):
                self.assert_current(target, trace["nodes"])
                self.assertEqual(trace["final"]["root"]["selectionEpoch"], trace["before"]["root"]["selectionEpoch"])
                self.assert_still(trace, target)
        self.finished = True

    def test_06_repeat_cancel_and_rapid_actions(self):
        self.launch()
        trace = self.observe("home_top_reclick", lambda: self.tap("home"))
        with self.e.check("A31"):
            self.assert_current("home", trace["nodes"])
            self.assertAlmostEqual(self.y(), 0, delta=1)
            self.assert_still(trace, "home")
        self.scroll_down()
        trace = self.observe("home_rapid_reclicks", lambda: [self.tap("home") for _ in range(5)])
        with self.e.check("A32"):
            self.assertCurrentHomeUnchanged(trace)
            self.assertAlmostEqual(self.y(), 0, delta=1)
            self.assertTrue(self.receive_visible(trace["nodes"]))
            self.assert_still(trace, "home")
        trace = self.observe("short_uncommitted_drag", lambda: self.driver.drag(
            (.50, .5), (.52, .5), area=BY.key("main_content_pager"), press_time=.2, drag_time=.5))
        with self.e.check("A35"):
            self.assertCurrentHomeUnchanged(trace)
            self.assert_still(trace, "home")
        # Already-running playback may continue; a same-home click must not start a second cycle.
        self.observe("go_me_before_running_home", lambda: self.tap("me"))

        def running_reclick():
            self.tap("home")
            time.sleep(.08)
            state = self.e.state("main_tab_home_icon")
            self.e.log({"runningRetapPrecondition": state, "time": time.monotonic()})
            if not state["ready"] or state["paused"] or state["frame"] <= 0:
                raise ObservationUnavailable("Running-home retap precondition missed; adjust timing and rerun")
            self.tap("home")

        trace = self.observe("return_then_reclick_running_home", running_reclick)
        with self.e.check("A28"):
            self.assert_current("home", trace["nodes"])
            self.assert_play(trace, "home")
        actions = [("tap", "category"), ("tap", "cart"), ("swipe", "LEFT"), ("tap", "home"),
                   ("tap", "me"), ("tap", "category"), ("tap", "home")]

        def mixed():
            for kind, value in actions:
                self.tap(value) if kind == "tap" else self.swipe(value)
                self.e.sample(all_icons=True)

        trace = self.observe("rapid_mixed_inputs", mixed)
        with self.e.check("A33"):
            self.assert_current("home", trace["nodes"])
            per_epoch = {}
            for sample in trace["states"]:
                root = sample.get("root", {})
                if root:
                    key = KEYS[int(root["selectedIndex"])]
                    if key in sample:
                        self.assertLessEqual(sample[key]["observedPlaySeq"], int(root["selectionEpoch"]))
                    for observed in KEYS:
                        if observed in sample:
                            engine = sample[observed]
                            entry = (observed, engine["consumedEpoch"])
                            per_epoch.setdefault(entry, []).append(engine["observedPlaySeq"])
            for entry, seqs in per_epoch.items():
                self.assertLessEqual(max(seqs) - min(seqs), 1, f"One consumed selection epoch started multiple playbacks: {entry}")
            before_sum = sum(trace["before"][k]["observedPlaySeq"] for k in KEYS)
            after_sum = sum(trace["final"][k]["observedPlaySeq"] for k in KEYS)
            commits = trace["final"]["root"]["selectionEpoch"] - trace["before"]["root"]["selectionEpoch"]
            self.assertLessEqual(after_sum - before_sum, commits, "Observed playbacks exceed actual accepted selection commits")
            self.assertTrue(trace["final"]["home"]["paused"])
        self.finished = True

    def assertCurrentHomeUnchanged(self, trace):
        self.assert_current("home", trace["nodes"])
        self.assertEqual(trace["final"]["root"]["selectionEpoch"], trace["before"]["root"]["selectionEpoch"])
        self.assertEqual(trace["final"]["root"]["instanceId"], trace["before"]["root"]["instanceId"])

    def test_07_empty_content_and_warm_restore(self):
        self.launch()
        for key in ("category", "cart", "me", "home"):
            trace = self.observe(f"local_content_{key}", lambda k=key: self.tap(k))
            with self.e.check("A36", "A37", details={"requestFailureInjection": "N/A: approved navigation/content implementation uses local data; no required request",
                                                        "emptyRemoteCategory": "N/A: category is fixed local content, with no remote data/empty response source"}):
                self.assert_current(key, trace["nodes"])
                self.assert_play(trace, key)
                if key == "cart":
                    self.visible_text("购物车空空如也")
                if key == "me":
                    self.visible_text("当前未登录")
        self.scroll_down()
        original_y = self.y()
        before = self.e.sample(all_icons=True)

        def warm():
            self.driver.press_home()
            time.sleep(.5)
            self.driver.start_app(self.bundle, page_name="EntryAbility", wait_time=0)

        trace = self.observe("warm_scrolled_home", warm)
        with self.e.check("A42", details={"subrouteReturn": "N/A: no approved reachable overlay route; normal background/foreground tested"}):
            self.assertCurrentHomeUnchanged(trace)
            self.assertAlmostEqual(self.y(), original_y, delta=2)
            self.assert_still(trace, "home")
            self.assertEqual(trace["final"]["root"]["instanceId"], before["root"]["instanceId"])
        self.observe("go_me_before_warm", lambda: self.tap("me"))
        trace = self.observe("warm_nonhome", warm)
        with self.e.check("A42"):
            self.assert_current("me", trace["nodes"])
            self.assertEqual(trace["final"]["root"], trace["before"]["root"])
            self.assert_still(trace, "me")
        self.finished = True

    def test_08_cold_restart_and_playback_interruption(self):
        self.launch()
        self.observe("go_me_before_cold", lambda: self.tap("me"))
        old_instance = self.e.state("main_root")["instanceId"]
        trace = self.launch(capture=True)
        with self.e.check("A38"):
            self.assert_current("home", trace["nodes"])
            self.assertNotEqual(trace["final"]["root"]["instanceId"], old_instance)
            self.assert_play(trace, "home")
        for target in ("category", "cart", "swipe"):
            self.observe(f"leave_before_interruption_{target}", lambda: self.tap("me"))

            def interrupt(k=target):
                self.tap("home")
                time.sleep(.08)
                active = self.e.state("main_tab_home_icon")
                self.e.log({"interruptionPrecondition": active, "target": k, "time": time.monotonic()})
                if not active["ready"] or active["paused"] or active["frame"] <= 0:
                    raise ObservationUnavailable("Animation interruption precondition missed; adjust action timing and rerun")
                self.swipe("LEFT") if k == "swipe" else self.tap(k)

            trace = self.observe(f"interrupt_home_{target}", interrupt)
            with self.e.check("A39"):
                self.assert_current("category" if target == "swipe" else target, trace["nodes"])
                self.assert_still(trace, "home", reset=True, compare_sequence=False)
                # Home was genuinely selected within this compound action, then stopped.
                self.assertEqual(trace["final"]["home"]["observedPlaySeq"] - trace["before"]["home"]["observedPlaySeq"], 1)
            trace = self.observe(f"return_after_interruption_{target}", lambda: self.tap("home"))
            with self.e.check("A39"):
                self.assert_play(trace, "home")
        self.finished = True
