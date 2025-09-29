"""
visualize_feedback.py
Visualizes trends from feedback_analytics.log (test failures, lint/type errors, etc.)
"""
import re
import matplotlib.pyplot as plt
from datetime import datetime

log_file = 'feedback_analytics.log'
pytest_pattern = re.compile(r'\[([^\]]+)\] Pytest exit code: (\d+)')
flake8_pattern = re.compile(r'\[([^\]]+)\] Flake8 exit code: (\d+)')
mypy_pattern = re.compile(r'\[([^\]]+)\] Mypy exit code: (\d+)')

def parse_log(pattern):
    times, codes = [], []
    with open(log_file) as f:
        for line in f:
            m = pattern.search(line)
            if m:
                times.append(datetime.fromisoformat(m.group(1)))
                codes.append(int(m.group(2)))
    return times, codes

def plot_trend(times, codes, label):
    plt.plot(times, codes, marker='o', label=label)

if __name__ == '__main__':
    plt.figure(figsize=(10,5))
    for pattern, label in [
        (pytest_pattern, 'pytest'),
        (flake8_pattern, 'flake8'),
        (mypy_pattern, 'mypy'),
    ]:
        times, codes = parse_log(pattern)
        if times:
            plot_trend(times, codes, label)
    plt.xlabel('Time')
    plt.ylabel('Exit Code (0=Success)')
    plt.title('Feedback Analytics Trends')
    plt.legend()
    plt.tight_layout()
    plt.show()
