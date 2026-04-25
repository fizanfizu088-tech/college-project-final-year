# responder.py
# Response generator — takes a detected intent and returns a formatted response.

from colorama import Fore, Style, init
from chatbot.data_store import (
    load_machines, load_inventory,
    get_low_stock_items, get_machines_by_status
)

init(autoreset=True)  # Colorama auto-reset after each print


# ─────────────────────────────────────────────
#  STATUS COLOR MAP
# ─────────────────────────────────────────────
STATUS_COLORS = {
    "running": Fore.GREEN,
    "idle":    Fore.YELLOW,
    "warning": Fore.RED,
    "offline": Fore.RED + Style.BRIGHT,
}

HEALTH_COLOR = lambda h: (
    Fore.GREEN if h >= 80 else
    Fore.YELLOW if h >= 50 else
    Fore.RED
)


def generate_response(intent: str) -> str:
    """
    Given an intent string, generate and return the appropriate response.
    Also prints a formatted version to the terminal.

    Returns:
        str: Plain text version of the response (for logging).
    """

    if intent == "greet":
        return _respond_greet()
    elif intent == "show_status":
        return _respond_status()
    elif intent == "machine_health":
        return _respond_health()
    elif intent == "inventory":
        return _respond_inventory()
    elif intent == "low_stock":
        return _respond_low_stock()
    elif intent == "maintenance":
        return _respond_maintenance()
    elif intent == "warnings":
        return _respond_warnings()
    elif intent == "offline":
        return _respond_offline()
    elif intent == "production":
        return _respond_production()
    elif intent == "help":
        return _respond_help()
    elif intent == "exit":
        return "EXIT"
    else:
        return _respond_unknown()


# ─────────────────────────────────────────────
#  INDIVIDUAL RESPONSE FUNCTIONS
# ─────────────────────────────────────────────

def _respond_greet():
    msg = "Hello! I am the NLI Manufacturing Assistant. How can I help you today?"
    print(Fore.CYAN + "\n[BOT] " + msg)
    return msg


def _respond_status():
    machines = load_machines()
    print(Fore.CYAN + "\n[BOT] Machine Status Report:")
    print(Fore.WHITE + "-" * 55)
    for m in machines:
        color = STATUS_COLORS.get(m["status"], Fore.WHITE)
        print(f"  {Fore.WHITE}{m['id']} | {m['name']:<20} | Status: {color}{m['status'].upper()}")
    print(Fore.WHITE + "-" * 55)
    return f"Status report shown for {len(machines)} machines."


def _respond_health():
    machines = load_machines()
    print(Fore.CYAN + "\n[BOT] Machine Health Report:")
    print(Fore.WHITE + "-" * 55)
    for m in machines:
        color = HEALTH_COLOR(m["health"])
        bar = _health_bar(m["health"])
        print(f"  {m['id']} | {m['name']:<20} | Health: {color}{bar} {m['health']}%")
    print(Fore.WHITE + "-" * 55)
    return f"Health report shown for {len(machines)} machines."


def _respond_inventory():
    inventory = load_inventory()
    print(Fore.CYAN + "\n[BOT] Inventory Report:")
    print(Fore.WHITE + "-" * 60)
    for item in inventory:
        color = Fore.RED if item["quantity"] < item["min_threshold"] else Fore.GREEN
        print(f"  {item['id']} | {item['item']:<20} | "
              f"Qty: {color}{item['quantity']} {item['unit']}{Fore.WHITE} "
              f"| Min: {item['min_threshold']}")
    print(Fore.WHITE + "-" * 60)
    return f"Inventory report shown for {len(inventory)} items."


def _respond_low_stock():
    low = get_low_stock_items()
    if not low:
        msg = "All inventory items are above their minimum thresholds."
        print(Fore.GREEN + "\n[BOT] " + msg)
        return msg
    print(Fore.CYAN + "\n[BOT] LOW STOCK ALERT:")
    print(Fore.WHITE + "-" * 55)
    for item in low:
        deficit = item["min_threshold"] - item["quantity"]
        print(f"  {Fore.RED}{item['item']:<22}{Fore.WHITE} | "
              f"Current: {item['quantity']} | "
              f"Need {deficit} more | Supplier: {item['supplier']}")
    print(Fore.WHITE + "-" * 55)
    return f"{len(low)} item(s) below minimum stock threshold."


def _respond_maintenance():
    machines = load_machines()
    print(Fore.CYAN + "\n[BOT] Maintenance Schedule:")
    print(Fore.WHITE + "-" * 60)
    for m in machines:
        print(f"  {m['id']} | {m['name']:<20} | "
              f"Last: {m['last_maintenance']} | "
              f"Next: {Fore.YELLOW}{m['next_maintenance']}")
    print(Fore.WHITE + "-" * 60)
    return f"Maintenance schedule shown for {len(machines)} machines."


def _respond_warnings():
    warning_machines = get_machines_by_status("warning")
    if not warning_machines:
        msg = "No machines currently in WARNING state."
        print(Fore.GREEN + "\n[BOT] " + msg)
        return msg
    print(Fore.RED + "\n[BOT] WARNING MACHINES:")
    print(Fore.WHITE + "-" * 55)
    for m in warning_machines:
        print(f"  {Fore.RED}{m['id']} | {m['name']:<20} | "
              f"Temp: {m['temperature']}C | Health: {m['health']}%")
    print(Fore.WHITE + "-" * 55)
    return f"{len(warning_machines)} machine(s) in WARNING state."


def _respond_offline():
    offline_machines = get_machines_by_status("offline")
    if not offline_machines:
        msg = "No machines are currently offline."
        print(Fore.GREEN + "\n[BOT] " + msg)
        return msg
    print(Fore.RED + Style.BRIGHT + "\n[BOT] OFFLINE MACHINES:")
    print(Fore.WHITE + "-" * 55)
    for m in offline_machines:
        print(f"  {m['id']} | {m['name']:<20} | Operator: {m['operator']}")
    print(Fore.WHITE + "-" * 55)
    return f"{len(offline_machines)} machine(s) offline."


def _respond_production():
    machines   = load_machines()
    running    = [m for m in machines if m["status"] == "running"]
    production = sum(m["health"] * 2 for m in running)   # simulated units

    print(Fore.CYAN + "\n[BOT] Production Summary:")
    print(Fore.WHITE + "-" * 45)
    print(f"  Active Machines  : {Fore.GREEN}{len(running)}")
    print(f"  {Fore.WHITE}Estimated Output : {Fore.GREEN}{production} units today")
    print(f"  {Fore.WHITE}Efficiency       : {Fore.GREEN}"
          f"{int((len(running)/len(machines))*100)}%")
    print(Fore.WHITE + "-" * 45)
    return f"Production summary: {len(running)} machines active, ~{production} units estimated."


def _respond_help():
    print(Fore.CYAN + "\n[BOT] Available Commands:")
    print(Fore.WHITE + "-" * 50)
    commands = [
        ("show status",    "View status of all machines"),
        ("machine health", "View health % of all machines"),
        ("inventory",      "View current stock levels"),
        ("low stock",      "Show items below minimum threshold"),
        ("maintenance",    "View maintenance schedule"),
        ("warnings",       "Show machines with warnings"),
        ("offline",        "Show offline machines"),
        ("production",     "View today's production estimate"),
        ("help",           "Show this help menu"),
        ("exit",           "Quit the chatbot"),
    ]
    for cmd, desc in commands:
        print(f"  {Fore.YELLOW}{cmd:<20}{Fore.WHITE} — {desc}")
    print(Fore.WHITE + "-" * 50)
    return "Help menu displayed."


def _respond_unknown():
    msg = ("I didn't understand that. Try: 'show status', 'inventory', "
           "'machine health', or type 'help' for all commands.")
    print(Fore.YELLOW + "\n[BOT] " + msg)
    return msg


# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────

def _health_bar(health: int, length: int = 10) -> str:
    """Generate a simple ASCII health bar."""
    filled = int((health / 100) * length)
    return "[" + "#" * filled + "-" * (length - filled) + "]"