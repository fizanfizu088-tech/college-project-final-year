# main.py (inside chatbot/)
# Core chatbot loop — handles user input, intent detection, response, and logging.

import time
from colorama import Fore, Style, init

from chatbot.matcher      import detect_intent
from chatbot.responder    import generate_response
from chatbot.logger       import setup_logger, log_interaction
from chatbot.performance  import PerformanceTracker

init(autoreset=True)

BANNER = """
╔══════════════════════════════════════════════════════╗
║   NLI Manufacturing Infrastructure Chatbot  v1.0    ║
║   Type 'help' for commands | 'exit' to quit         ║
╚══════════════════════════════════════════════════════╝
"""


def run_chatbot():
    """Main chatbot loop."""
    logger  = setup_logger()
    tracker = PerformanceTracker()

    print(Fore.CYAN + BANNER)
    logger.info("Chatbot session started.")

    while True:
        try:
            # ── Get user input
            user_input = input(Fore.GREEN + "\n[YOU] > " + Style.RESET_ALL).strip()

            if not user_input:
                continue   # ignore blank input

            # ── Detect intent
            start_time = time.perf_counter()
            intent     = detect_intent(user_input)
            end_time   = time.perf_counter()

            response_time_ms = (end_time - start_time) * 1000
            matched          = intent != "unknown"

            # ── Generate response
            response = generate_response(intent)

            # ── Handle exit
            if response == "EXIT":
                print(Fore.CYAN + "\n[BOT] Goodbye! Stay safe on the factory floor.")
                tracker.print_report()
                logger.info("Chatbot session ended by user.")
                break

            # ── Log the interaction
            log_interaction(logger, user_input, response, response_time_ms, matched)

            # ── Record performance
            tracker.record(matched, response_time_ms)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n[BOT] Session interrupted. Printing report...")
            tracker.print_report()
            break

        except Exception as e:
            print(Fore.RED + f"\n[ERROR] Something went wrong: {e}")
            logger.error(f"Unexpected error: {e}")