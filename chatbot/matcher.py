# matcher.py
# Keyword-based intent detection engine.
# Maps user input strings to intent labels using keyword lists.

# ─────────────────────────────────────────────
#  INTENT → KEYWORDS mapping
#  Order matters: more specific intents must come FIRST.
#  Multi-word phrases are checked before single words.
# ─────────────────────────────────────────────
INTENT_KEYWORDS = {
    "show_status": [
        "show status", "machine status", "all status", "status report",
        "overall status", "factory status", "floor status",
        "what is running", "what machines are on"
    ],
    "machine_health": [
        "machine health", "health report", "health status",
        "check health", "machine condition", "equipment health",
        "how are the machines", "machine performance"
    ],
    "low_stock": [
        "low stock", "running low", "shortage", "restock",
        "below threshold", "critical stock", "out of stock",
        "what needs restocking", "stock alert"
    ],
    "inventory": [
        "inventory", "stock", "supplies", "materials",
        "check inventory", "show inventory", "stock level",
        "how much stock", "what do we have"
    ],
    "maintenance": [
        "maintenance", "service", "repair", "due for service",
        "maintenance schedule", "next service", "overdue",
        "needs repair", "maintenance due"
    ],
    "warnings": [
        "warning", "alert", "fault", "issue", "problem",
        "error", "critical", "danger", "unsafe",
        "what is wrong", "any faults"
    ],
    "offline": [
        "offline", "down", "not working", "stopped",
        "machine down", "out of service", "shutdown"
    ],
    "production": [
        "production", "output", "today output", "production rate",
        "how much produced", "units made", "daily output"
    ],
    "help": [
        "help", "commands", "what can you do", "options",
        "menu", "guide", "how to use", "instructions"
    ],
    "greet": [
        "hello", "hi", "hey", "good morning", "good afternoon",
        "good evening", "howdy", "greetings"
    ],
    "exit": [
        "exit", "quit", "bye", "goodbye", "close",
        "stop", "end", "shutdown chatbot", "see you"
    ],
}


def detect_intent(user_input: str) -> str:
    """
    Detect intent from user input using keyword matching.

    Steps:
    1. Normalize input to lowercase.
    2. First pass: check only multi-word phrases (length > 1 word).
    3. Second pass: check single-word keywords.
    4. Return 'unknown' if nothing matches.

    Returns:
        str: Intent label (e.g. 'show_status', 'inventory', 'unknown')
    """
    text = user_input.lower().strip()

    # First pass — multi-word phrases only (more specific, checked first)
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if len(keyword.split()) > 1 and keyword in text:
                return intent

    # Second pass — single-word keywords
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if len(keyword.split()) == 1 and keyword in text:
                return intent

    return "unknown"


def get_all_intents() -> list:
    """Return a list of all supported intent names."""
    return list(INTENT_KEYWORDS.keys())