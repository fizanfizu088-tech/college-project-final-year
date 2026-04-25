# test_chatbot.py
# Unit tests for the NLI Manufacturing Chatbot.
# Run with: python -m pytest tests/ -v

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.matcher import detect_intent, get_all_intents
from chatbot.data_store import (
    load_machines, load_inventory,
    get_low_stock_items, get_machines_by_status,
    get_machine_by_id
)
from chatbot.performance import PerformanceTracker


# ─────────────────────────────────────────────
#  INTENT DETECTION TESTS
# ─────────────────────────────────────────────

class TestIntentDetection:

    def test_greet_hello(self):
        assert detect_intent("hello") == "greet"

    def test_greet_hi(self):
        assert detect_intent("hi there") == "greet"

    def test_show_status(self):
        assert detect_intent("show status") == "show_status"

    def test_show_status_variation(self):
        assert detect_intent("give me the machine status") == "show_status"

    def test_machine_health(self):
        assert detect_intent("machine health") == "machine_health"

    def test_machine_health_variation(self):
        assert detect_intent("check health of machines") == "machine_health"

    def test_inventory(self):
        assert detect_intent("inventory") == "inventory"

    def test_inventory_variation(self):
        assert detect_intent("show me the stock") == "inventory"

    def test_low_stock(self):
        assert detect_intent("low stock") == "low_stock"

    def test_low_stock_variation(self):
        assert detect_intent("what needs restocking") == "low_stock"

    def test_maintenance(self):
        assert detect_intent("maintenance schedule") == "maintenance"

    def test_maintenance_variation(self):
        assert detect_intent("which machines need service") == "maintenance"

    def test_warnings(self):
        assert detect_intent("any warnings") == "warnings"

    def test_offline(self):
        assert detect_intent("show offline machines") == "offline"

    def test_production(self):
        assert detect_intent("production output") == "production"

    def test_help(self):
        assert detect_intent("help") == "help"

    def test_exit(self):
        assert detect_intent("exit") == "exit"

    def test_exit_bye(self):
        assert detect_intent("bye") == "exit"

    def test_unknown(self):
        assert detect_intent("xyzabc123") == "unknown"

    def test_unknown_gibberish(self):
        assert detect_intent("   ") == "unknown"

    def test_case_insensitive(self):
        assert detect_intent("SHOW STATUS") == "show_status"

    def test_case_insensitive_health(self):
        assert detect_intent("MACHINE HEALTH") == "machine_health"

    def test_low_stock_beats_inventory(self):
        # "low stock" contains "stock" — must match low_stock not inventory
        assert detect_intent("low stock alert") == "low_stock"


# ─────────────────────────────────────────────
#  DATA STORE TESTS
# ─────────────────────────────────────────────

class TestDataStore:

    def test_load_machines_returns_list(self):
        machines = load_machines()
        assert isinstance(machines, list)

    def test_load_machines_count(self):
        machines = load_machines()
        assert len(machines) == 5

    def test_machine_has_required_fields(self):
        machines = load_machines()
        required = {"id", "name", "status", "health", "temperature",
                    "last_maintenance", "next_maintenance", "operator"}
        for m in machines:
            assert required.issubset(m.keys())

    def test_load_inventory_returns_list(self):
        inventory = load_inventory()
        assert isinstance(inventory, list)

    def test_load_inventory_count(self):
        inventory = load_inventory()
        assert len(inventory) == 5

    def test_inventory_has_required_fields(self):
        inventory = load_inventory()
        required = {"id", "item", "quantity", "unit",
                    "min_threshold", "supplier", "last_restocked"}
        for item in inventory:
            assert required.issubset(item.keys())

    def test_get_machine_by_id_found(self):
        machine = get_machine_by_id("M001")
        assert machine is not None
        assert machine["name"] == "CNC Lathe"

    def test_get_machine_by_id_not_found(self):
        machine = get_machine_by_id("M999")
        assert machine is None

    def test_get_machine_by_id_case_insensitive(self):
        machine = get_machine_by_id("m001")
        assert machine is not None

    def test_get_low_stock_items(self):
        low = get_low_stock_items()
        assert isinstance(low, list)
        # Hydraulic Oil (45 < 50) and Welding Wire (12 < 20) are low
        assert len(low) == 2

    def test_low_stock_items_are_actually_low(self):
        low = get_low_stock_items()
        for item in low:
            assert item["quantity"] < item["min_threshold"]

    def test_get_machines_by_status_running(self):
        running = get_machines_by_status("running")
        assert len(running) == 2

    def test_get_machines_by_status_offline(self):
        offline = get_machines_by_status("offline")
        assert len(offline) == 1
        assert offline[0]["id"] == "M005"

    def test_get_machines_by_status_warning(self):
        warning = get_machines_by_status("warning")
        assert len(warning) == 1
        assert warning[0]["id"] == "M003"

    def test_machine_health_range(self):
        machines = load_machines()
        for m in machines:
            assert 0 <= m["health"] <= 100


# ─────────────────────────────────────────────
#  PERFORMANCE TRACKER TESTS
# ─────────────────────────────────────────────

class TestPerformanceTracker:

    def test_initial_state(self):
        tracker = PerformanceTracker()
        assert tracker.total_queries == 0
        assert tracker.matched_queries == 0
        assert tracker.response_times == []

    def test_record_matched(self):
        tracker = PerformanceTracker()
        tracker.record(matched=True, response_time_ms=1.5)
        assert tracker.total_queries == 1
        assert tracker.matched_queries == 1

    def test_record_unmatched(self):
        tracker = PerformanceTracker()
        tracker.record(matched=False, response_time_ms=0.8)
        assert tracker.total_queries == 1
        assert tracker.matched_queries == 0

    def test_accuracy_100(self):
        tracker = PerformanceTracker()
        tracker.record(True, 1.0)
        tracker.record(True, 2.0)
        assert tracker.accuracy() == 100.0

    def test_accuracy_50(self):
        tracker = PerformanceTracker()
        tracker.record(True, 1.0)
        tracker.record(False, 1.0)
        assert tracker.accuracy() == 50.0

    def test_accuracy_zero_queries(self):
        tracker = PerformanceTracker()
        assert tracker.accuracy() == 0.0

    def test_avg_response_time(self):
        tracker = PerformanceTracker()
        tracker.record(True, 2.0)
        tracker.record(True, 4.0)
        assert tracker.avg_response_time() == 3.0

    def test_max_response_time(self):
        tracker = PerformanceTracker()
        tracker.record(True, 1.0)
        tracker.record(True, 9.5)
        tracker.record(True, 3.0)
        assert tracker.max_response_time() == 9.5

    def test_session_duration_positive(self):
        tracker = PerformanceTracker()
        assert tracker.session_duration() >= 0