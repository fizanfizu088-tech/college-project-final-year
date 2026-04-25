# performance.py
# Tracks and evaluates chatbot performance metrics.

import time


class PerformanceTracker:
    """
    Tracks chatbot session metrics:
    - Total queries processed
    - Matched vs unmatched queries
    - Response times
    """

    def __init__(self):
        self.total_queries    = 0
        self.matched_queries  = 0
        self.response_times   = []   # list of floats (milliseconds)
        self.session_start    = time.time()

    def record(self, matched: bool, response_time_ms: float):
        """Record one interaction."""
        self.total_queries += 1
        if matched:
            self.matched_queries += 1
        self.response_times.append(response_time_ms)

    def accuracy(self) -> float:
        """Return match accuracy as a percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.matched_queries / self.total_queries) * 100

    def avg_response_time(self) -> float:
        """Return average response time in milliseconds."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def max_response_time(self) -> float:
        """Return maximum (slowest) response time."""
        return max(self.response_times) if self.response_times else 0.0

    def session_duration(self) -> float:
        """Return total session duration in seconds."""
        return time.time() - self.session_start

    def print_report(self):
        """Print a formatted performance evaluation report."""
        from colorama import Fore, Style, init
        init(autoreset=True)

        print(Fore.CYAN + "\n" + "=" * 50)
        print(Fore.CYAN + "     PERFORMANCE EVALUATION REPORT")
        print(Fore.CYAN + "=" * 50)
        print(f"  Total Queries      : {Fore.WHITE}{self.total_queries}")
        print(f"  Matched Queries    : {Fore.GREEN}{self.matched_queries}")
        print(f"  Unmatched Queries  : {Fore.RED}"
              f"{self.total_queries - self.matched_queries}")
        print(f"  {Fore.WHITE}Match Accuracy     : "
              f"{Fore.GREEN}{self.accuracy():.1f}%")
        print(f"  {Fore.WHITE}Avg Response Time  : "
              f"{Fore.YELLOW}{self.avg_response_time():.2f} ms")
        print(f"  {Fore.WHITE}Max Response Time  : "
              f"{Fore.YELLOW}{self.max_response_time():.2f} ms")
        print(f"  {Fore.WHITE}Session Duration   : "
              f"{Fore.WHITE}{self.session_duration():.1f} seconds")
        print(Fore.CYAN + "=" * 50 + "\n")