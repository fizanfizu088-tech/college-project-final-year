# data_store.py
# Loads and provides access to manufacturing data (machines + inventory)

import json
import os

# Resolve paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACHINES_FILE  = os.path.join(BASE_DIR, "data", "machines.json")
INVENTORY_FILE = os.path.join(BASE_DIR, "data", "inventory.json")


def load_machines():
    """Load and return machine data from JSON file."""
    with open(MACHINES_FILE, "r") as f:
        return json.load(f)["machines"]


def load_inventory():
    """Load and return inventory data from JSON file."""
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)["inventory"]


def get_machine_by_id(machine_id):
    """Return a single machine dict by its ID (e.g. 'M001'), or None."""
    machines = load_machines()
    for m in machines:
        if m["id"].upper() == machine_id.upper():
            return m
    return None


def get_low_stock_items():
    """Return list of inventory items below their minimum threshold."""
    inventory = load_inventory()
    return [item for item in inventory if item["quantity"] < item["min_threshold"]]


def get_machines_by_status(status):
    """Return machines matching a given status string (running/idle/warning/offline)."""
    machines = load_machines()
    return [m for m in machines if m["status"].lower() == status.lower()]